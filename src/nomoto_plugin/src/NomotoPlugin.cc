#include "nomoto_plugin/NomotoPlugin.hh"

#include <chrono>
#include <cmath>

#include <gz/plugin/Register.hh>
#include <gz/sim/Link.hh>
#include <gz/math/Vector3.hh>

using namespace nomoto_plugin;

void NomotoPlugin::Configure(
  const gz::sim::Entity &_entity,
  const std::shared_ptr<const sdf::Element> &_sdf,
  gz::sim::EntityComponentManager &_ecm,
  gz::sim::EventManager &)
{
  this->model = gz::sim::Model(_entity);

  if (_sdf->HasElement("T"))
    this->T = _sdf->Get<double>("T");

  if (_sdf->HasElement("K"))
    this->K = _sdf->Get<double>("K");

  std::string linkName = "base_link";
  if (_sdf->HasElement("link_name"))
    linkName = _sdf->Get<std::string>("link_name");

  this->baseLink = this->model.LinkByName(_ecm, linkName);

  if (!rclcpp::ok())
  {
    int argc = 0;
    char **argv = nullptr;
    rclcpp::init(argc, argv);
  }

  this->rosNode = rclcpp::Node::make_shared("nomoto_gazebo_plugin");

  this->rudderSub = this->rosNode->create_subscription<std_msgs::msg::Float64>(
    "/asv/rudder_cmd",
    10,
    [this](const std_msgs::msg::Float64::SharedPtr msg)
    {
      this->rudderCmdDeg = msg->data;   // already radians
    });

  RCLCPP_INFO(this->rosNode->get_logger(), "Yaw-only Nomoto plugin loaded");
}

void NomotoPlugin::PreUpdate(
  const gz::sim::UpdateInfo &_info,
  gz::sim::EntityComponentManager &_ecm)
{
  if (_info.paused)
    return;

  rclcpp::spin_some(this->rosNode);

  double dt = std::chrono::duration<double>(_info.dt).count();
  if (dt <= 0.0)
    return;

  double delta = this->rudderCmdDeg;  // radians

  double rDot = (this->K * delta - this->r) / this->T;
  this->r += rDot * dt;

  gz::sim::Link link(this->baseLink);

  // Only yaw is controlled by Nomoto.
  // Do not overwrite surge, heave, roll, or pitch.
  link.SetAngularVelocity(_ecm, gz::math::Vector3d(0.0, 0.0, this->r));
}

GZ_ADD_PLUGIN(
  NomotoPlugin,
  gz::sim::System,
  NomotoPlugin::ISystemConfigure,
  NomotoPlugin::ISystemPreUpdate
)
