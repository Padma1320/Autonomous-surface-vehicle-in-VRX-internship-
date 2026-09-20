#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Link.hh>
#include <gz/sim/Entity.hh>

#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>

#include <sdf/Element.hh>

#include <string>

namespace asv
{

class ASVDVLPlugin:
  public gz::sim::System,
  public gz::sim::ISystemConfigure,
  public gz::sim::ISystemPostUpdate
{
public:
  ASVDVLPlugin() = default;

  void Configure(
    const gz::sim::Entity &_entity,
    const std::shared_ptr<const sdf::Element> &_sdf,
    gz::sim::EntityComponentManager &_ecm,
    gz::sim::EventManager &) override
  {
    this->model = gz::sim::Model(_entity);

    if (_sdf->HasElement("topic"))
      this->topic = _sdf->Get<std::string>("topic");

    if (_sdf->HasElement("link_name"))
      this->link_name = _sdf->Get<std::string>("link_name");

    auto link_entity = this->model.LinkByName(_ecm, this->link_name);

    if (link_entity == gz::sim::kNullEntity)
    {
      gzerr << "[ASVDVLPlugin] Link not found: "
            << this->link_name << std::endl;
      return;
    }

    this->link = gz::sim::Link(link_entity);

    // This tells Gazebo to compute velocity components for this link
    this->link.EnableVelocityChecks(_ecm, true);

    this->pub = this->node.Advertise<gz::msgs::Twist>(this->topic);

    gzmsg << "[ASVDVLPlugin] Loaded for model: "
          << this->model.Name(_ecm)
          << " | Link: " << this->link_name
          << " | Publishing: " << this->topic
          << std::endl;
  }

  void PostUpdate(
    const gz::sim::UpdateInfo &_info,
    const gz::sim::EntityComponentManager &_ecm) override
  {
    if (_info.paused)
      return;

    auto world_vel_opt = this->link.WorldLinearVelocity(_ecm);
    auto world_pose_opt = this->link.WorldPose(_ecm);

    if (!world_vel_opt || !world_pose_opt)
      return;

    auto world_vel = world_vel_opt.value();
    auto world_pose = world_pose_opt.value();

    // Convert world-frame velocity to body-frame velocity
    // DVL frame:
    // x = forward
    // y = sideways
    // z = vertical
    auto body_vel = world_pose.Rot().Inverse().RotateVector(world_vel);

    gz::msgs::Twist msg;

    msg.mutable_linear()->set_x(body_vel.X());
    msg.mutable_linear()->set_y(body_vel.Y());
    msg.mutable_linear()->set_z(body_vel.Z());

    this->pub.Publish(msg);
  }

private:
  gz::sim::Model model{gz::sim::kNullEntity};
  gz::sim::Link link{gz::sim::kNullEntity};

  gz::transport::Node node;
  gz::transport::Node::Publisher pub;

  std::string topic{"/asv/dvl/velocity_gz"};
  std::string link_name{"base_link"};
};

}

GZ_ADD_PLUGIN(
  asv::ASVDVLPlugin,
  gz::sim::System,
  asv::ASVDVLPlugin::ISystemConfigure,
  asv::ASVDVLPlugin::ISystemPostUpdate
)
