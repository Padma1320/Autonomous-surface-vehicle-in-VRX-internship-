#ifndef NOMOTO_PLUGIN_HH_
#define NOMOTO_PLUGIN_HH_

#include <memory>
#include <string>

#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Entity.hh>

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64.hpp>

namespace nomoto_plugin
{
class NomotoPlugin:
  public gz::sim::System,
  public gz::sim::ISystemConfigure,
  public gz::sim::ISystemPreUpdate
{
public:
  void Configure(
    const gz::sim::Entity &_entity,
    const std::shared_ptr<const sdf::Element> &_sdf,
    gz::sim::EntityComponentManager &_ecm,
    gz::sim::EventManager &_eventMgr) override;

  void PreUpdate(
    const gz::sim::UpdateInfo &_info,
    gz::sim::EntityComponentManager &_ecm) override;

private:
  gz::sim::Model model{gz::sim::kNullEntity};
  gz::sim::Entity baseLink{gz::sim::kNullEntity};

  rclcpp::Node::SharedPtr rosNode;
  rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr thrustSub;
  rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr rudderSub;

  double T{2.5};
  double K{0.15};
  double maxThrust{30.0};
  double maxSpeed{0.3};

  double thrustCmd{0.0};
  double rudderCmdDeg{0.0};
  double r{0.0};
  double u{0.0};
  double thrustUsed{0.0};
  double thrustRateLimit{10.0};
};
}

#endif
