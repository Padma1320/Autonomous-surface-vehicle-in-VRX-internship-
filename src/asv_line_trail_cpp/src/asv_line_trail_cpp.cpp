#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/path.hpp"

#include <gz/transport/Node.hh>
#include <gz/msgs/marker.pb.h>


class ASVLineTrail : public rclcpp::Node
{
public:
  ASVLineTrail() : Node("asv_line_trail_cpp")
  {
    gz_pub_ = gz_node_.Advertise<gz::msgs::Marker>("/marker");

    path_sub_ = this->create_subscription<nav_msgs::msg::Path>(
      "/asv/path",
      10,
      std::bind(&ASVLineTrail::pathCallback, this, std::placeholders::_1)
    );

    RCLCPP_INFO(this->get_logger(), "ASV Gazebo LINE_STRIP trail started");
  }

private:
  void pathCallback(const nav_msgs::msg::Path::SharedPtr msg)
  {
    if (msg->poses.size() < 2)
      return;

    gz::msgs::Marker marker;

    marker.set_ns("asv_path_line");
    marker.set_id(1);
    marker.set_action(gz::msgs::Marker::ADD_MODIFY);
    marker.set_type(gz::msgs::Marker::LINE_STRIP);

    marker.mutable_material()->mutable_diffuse()->set_r(1.0);
    marker.mutable_material()->mutable_diffuse()->set_g(0.0);
    marker.mutable_material()->mutable_diffuse()->set_b(0.0);
    marker.mutable_material()->mutable_diffuse()->set_a(1.0);

    marker.mutable_material()->mutable_emissive()->set_r(1.0);
    marker.mutable_material()->mutable_emissive()->set_g(0.0);
    marker.mutable_material()->mutable_emissive()->set_b(0.0);
    marker.mutable_material()->mutable_emissive()->set_a(1.0);

    marker.mutable_scale()->set_x(0.15);

    for (const auto & pose_stamped : msg->poses)
    {
      auto point = marker.add_point();

      point->set_x(pose_stamped.pose.position.x);
      point->set_y(pose_stamped.pose.position.y);
      point->set_z(0.6);
    }

    gz_pub_.Publish(marker);

    RCLCPP_INFO(
      this->get_logger(),
      "Published Gazebo LINE_STRIP with %ld points",
      msg->poses.size()
    );
  }

  rclcpp::Subscription<nav_msgs::msg::Path>::SharedPtr path_sub_;

  gz::transport::Node gz_node_;
  gz::transport::Node::Publisher gz_pub_;
};


int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ASVLineTrail>());
  rclcpp::shutdown();
  return 0;
}
