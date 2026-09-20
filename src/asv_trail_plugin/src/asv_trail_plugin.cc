#include <cmath>
#include <string>

#include <gz/plugin/Register.hh>
#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/Pose.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/entity_factory.pb.h>
#include <gz/msgs/boolean.pb.h>

namespace asv_trail_plugin
{
class ASVTrailPlugin:
  public gz::sim::System,
  public gz::sim::ISystemConfigure,
  public gz::sim::ISystemPostUpdate
{
public:
  void Configure(
    const gz::sim::Entity &_entity,
    const std::shared_ptr<const sdf::Element> &_sdf,
    gz::sim::EntityComponentManager &,
    gz::sim::EventManager &) override
  {
    this->modelEntity = _entity;

    if (_sdf->HasElement("min_distance"))
      this->minDistance = _sdf->Get<double>("min_distance");

    if (_sdf->HasElement("z"))
      this->zHeight = _sdf->Get<double>("z");

    if (_sdf->HasElement("size"))
      this->boxSize = _sdf->Get<double>("size");
  }

  void PostUpdate(
    const gz::sim::UpdateInfo &_info,
    const gz::sim::EntityComponentManager &_ecm) override
  {
    if (_info.paused)
      return;

    auto poseComp = _ecm.Component<gz::sim::components::Pose>(this->modelEntity);

    if (!poseComp)
      return;

    auto pose = poseComp->Data();

    double x = pose.Pos().X();
    double y = pose.Pos().Y();

    if (!this->hasLast)
    {
      this->lastX = x;
      this->lastY = y;
      this->hasLast = true;
      this->SpawnTrailCube(x, y);
      return;
    }

    double dx = x - this->lastX;
    double dy = y - this->lastY;
    double dist = std::sqrt(dx * dx + dy * dy);

    if (dist < this->minDistance)
      return;

    this->SpawnTrailCube(x, y);

    this->lastX = x;
    this->lastY = y;
  }

private:
  void SpawnTrailCube(double x, double y)
  {
    std::string name = "asv_direct_trail_" + std::to_string(this->count++);

    std::string sdf =
      "<sdf version='1.9'>"
      "<model name='" + name + "'>"
      "<static>true</static>"
      "<pose>" + std::to_string(x) + " " + std::to_string(y) + " " + std::to_string(this->zHeight) + " 0 0 0</pose>"
      "<link name='link'>"
      "<visual name='visual'>"
      "<geometry>"
      "<box><size>" + std::to_string(this->boxSize) + " " + std::to_string(this->boxSize) + " " + std::to_string(this->boxSize) + "</size></box>"
      "</geometry>"
      "<material>"
      "<ambient>1 0 0 1</ambient>"
      "<diffuse>1 0 0 1</diffuse>"
      "<emissive>1 0 0 1</emissive>"
      "</material>"
      "</visual>"
      "</link>"
      "</model>"
      "</sdf>";

    gz::msgs::EntityFactory req;
    gz::msgs::Boolean rep;
    bool result = false;

    req.set_sdf(sdf);
    req.set_name(name);

    this->node.Request(
      "/world/sydney_regatta/create",
      req,
      1000,
      rep,
      result
    );
  }

private:
  gz::sim::Entity modelEntity;
  gz::transport::Node node;

  bool hasLast{false};
  double lastX{0.0};
  double lastY{0.0};

  double minDistance{0.5};
  double zHeight{0.7};
  double boxSize{0.25};

  int count{0};
};
}

GZ_ADD_PLUGIN(
  asv_trail_plugin::ASVTrailPlugin,
  gz::sim::System,
  asv_trail_plugin::ASVTrailPlugin::ISystemConfigure,
  asv_trail_plugin::ASVTrailPlugin::ISystemPostUpdate
)

GZ_ADD_PLUGIN_ALIAS(
  asv_trail_plugin::ASVTrailPlugin,
  "asv_trail_plugin::ASVTrailPlugin"
)
