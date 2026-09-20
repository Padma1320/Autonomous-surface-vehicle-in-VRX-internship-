#include <rclcpp/rclcpp.hpp>
#include <GeographicLib/LocalCartesian.hpp>
#include <nav_msgs/msg/path.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>

#include <gz/transport/Node.hh>
#include <gz/msgs/vector3d.pb.h>

#include <cmath>
#include <cstdlib>
#include <sstream>
#include <vector>
#include <thread>
#include <utility>
#include <functional>

class GzWaypointBridge : public rclcpp::Node
{
public:
  GzWaypointBridge() : Node("gz_waypoint_bridge")
  {
    path_pub_ = this->create_publisher<nav_msgs::msg::Path>(
      "/asv/waypoints",
      10
    );

    gps_path_pub_ = this->create_publisher<nav_msgs::msg::Path>(
      "/asv/waypoints_gps",
      10
    );

    gps_sub_ = this->create_subscription<sensor_msgs::msg::NavSatFix>(
      "/asv/gps_data",
      10,
      std::bind(&GzWaypointBridge::gpsCallback, this, std::placeholders::_1)
    );

    gz_node_.Subscribe(
      "/asv/gz_clicked_waypoint",
      &GzWaypointBridge::gzClickCallback,
      this
    );

    RCLCPP_INFO(
      this->get_logger(),
      "Listening to Gazebo clicks on /asv/gz_clicked_waypoint"
    );

    RCLCPP_INFO(
      this->get_logger(),
      "Subscribing GPS origin from /asv/gps_data"
    );

    RCLCPP_INFO(
      this->get_logger(),
      "Publishing ROS2 waypoints on /asv/waypoints and /asv/waypoints_gps"
    );
  }

private:
  bool gps_origin_set_ = false;
  bool has_prev_wp_ = false;
  double prev_x_ = 0.0;
  double prev_y_ = 0.0;
  double origin_lat_ = 0.0;
  double origin_lon_ = 0.0;
  GeographicLib::LocalCartesian geo_converter_;

  std::vector<std::pair<double, double>> waypoints_;
  std::vector<std::pair<double, double>> gps_waypoints_;

  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr path_pub_;
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr gps_path_pub_;
  rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr gps_sub_;

  gz::transport::Node gz_node_;

  void gpsCallback(const sensor_msgs::msg::NavSatFix::SharedPtr msg)
  {
    if (!gps_origin_set_)
    {
      origin_lat_ = msg->latitude;
      origin_lon_ = msg->longitude;
      gps_origin_set_ = true;
      geo_converter_.Reset(origin_lat_, origin_lon_, 0.0);

      RCLCPP_INFO(
        this->get_logger(),
        "GPS origin set from /asv/gps_data: LAT=%.8f LON=%.8f",
        origin_lat_,
        origin_lon_
      );
    }
  }

  void xyToLatLon(double x, double y, double &lat, double &lon)
{
  double alt = 0.0;

  // x = East, y = North, z = Up
  geo_converter_.Reverse(
    x,
    y,
    0.0,
    lat,
    lon,
    alt
  );
}

  void gzClickCallback(const gz::msgs::Vector3d &_msg)
  {
    if (!gps_origin_set_)
    {
      RCLCPP_WARN(
        this->get_logger(),
        "Ignored waypoint click: GPS origin not received yet from /asv/gps_data"
      );
      return;
    }

    const double x = _msg.x();
    const double y = _msg.y();
    const double z = 0.0;

    waypoints_.push_back({x, y});
    const int wp_id = static_cast<int>(waypoints_.size());

    double lat = 0.0;
    double lon = 0.0;
    xyToLatLon(x, y, lat, lon);

    gps_waypoints_.push_back({lat, lon});

    RCLCPP_INFO(
      this->get_logger(),
      "WP%d: X=%.2f Y=%.2f Z=%.2f | LAT=%.8f LON=%.8f",
      wp_id,
      x,
      y,
      z,
      lat,
      lon
    );

    publishPath();
    publishGpsPath();

   std::thread([this, wp_id, x, y]() {
  this->spawnMarker(wp_id, x, y);

  if (this->has_prev_wp_)
  {
    this->spawnConnector(wp_id, this->prev_x_, this->prev_y_, x, y);
  }

  this->prev_x_ = x;
  this->prev_y_ = y;
  this->has_prev_wp_ = true;
}).detach();
  }

 void spawnMarker(int wp_id, double x, double y)
{
  std::stringstream ss;

  ss << "gz service -s /world/sydney_regatta/create "
     << "--reqtype gz.msgs.EntityFactory "
     << "--reptype gz.msgs.Boolean "
     << "--timeout 10000 "
     << "--req 'sdf:\"<sdf version=\\\"1.9\\\">"

     << "<model name=\\\"waypoint_marker_" << wp_id << "\\\">"
     << "<static>true</static>"
     << "<pose>" << x << " " << y << " 1.2 0 0 0</pose>"

     << "<link name=\\\"link\\\">"

     << "<visual name=\\\"map_waypoint_visual\\\">"
     << "<pose>0 0 0 1.5708 0 1.5708</pose>"
     << "<geometry>"
     << "<mesh>"
     << "<uri>file:///home/user/vrx_ws/src/vrx/vrx_gz/models/my_asv/meshes/map_waypoint_centered.STL</uri>"
     << "<scale>0.05 0.05 0.05</scale>"
     << "</mesh>"
     << "</geometry>"
     << "</visual>"

     << "</link>"
     << "</model>"
     << "</sdf>\", name:\"waypoint_marker_" << wp_id << "\"'";

  std::system(ss.str().c_str());
}
  void spawnConnector(int wp_id, double x1, double y1, double x2, double y2)
{
  double dx = x2 - x1;
  double dy = y2 - y1;

  double length = std::sqrt(dx * dx + dy * dy);
  double mid_x = (x1 + x2) / 2.0;
  double mid_y = (y1 + y2) / 2.0;
  double yaw = std::atan2(dy, dx);

  std::stringstream ss;

  ss << "gz service -s /world/sydney_regatta/create "
     << "--reqtype gz.msgs.EntityFactory "
     << "--reptype gz.msgs.Boolean "
     << "--timeout 10000 "
     << "--req 'sdf:\"<sdf version=\\\"1.9\\\">"
     << "<model name=\\\"waypoint_connector_" << wp_id << "\\\">"
     << "<static>true</static>"
     << "<pose>" << mid_x << " " << mid_y << " 0.08 0 0 " << yaw << "</pose>"
     << "<link name=\\\"link\\\">"
     << "<visual name=\\\"red_connector_visual\\\">"
     << "<geometry>"
     << "<box>"
     << "<size>" << length << " 0.12 0.05</size>"
     << "</box>"
     << "</geometry>"
     << "<material>"
     << "<ambient>1 0 0 1</ambient>"
     << "<diffuse>1 0 0 1</diffuse>"
     << "<emissive>0.5 0 0 1</emissive>"
     << "</material>"
     << "</visual>"
     << "</link>"
     << "</model>"
     << "</sdf>\", name:\"waypoint_connector_" << wp_id << "\"'";

  std::system(ss.str().c_str());
}
  void publishPath()
  {
    nav_msgs::msg::Path path;
    path.header.frame_id = "map";
    path.header.stamp = this->now();

    for (auto &wp : waypoints_)
    {
      geometry_msgs::msg::PoseStamped pose;
      pose.header.frame_id = "map";
      pose.header.stamp = this->now();

      pose.pose.position.x = wp.first;
      pose.pose.position.y = wp.second;
      pose.pose.position.z = 0.0;
      pose.pose.orientation.w = 1.0;

      path.poses.push_back(pose);
    }

    path_pub_->publish(path);
  }

  void publishGpsPath()
  {
    nav_msgs::msg::Path gps_path;
    gps_path.header.frame_id = "wgs84";
    gps_path.header.stamp = this->now();

    for (auto &wp : gps_waypoints_)
    {
      geometry_msgs::msg::PoseStamped pose;
      pose.header.frame_id = "wgs84";
      pose.header.stamp = this->now();

      pose.pose.position.x = wp.first;
      pose.pose.position.y = wp.second;
      pose.pose.position.z = 0.0;
      pose.pose.orientation.w = 1.0;

      gps_path.poses.push_back(pose);
    }

    gps_path_pub_->publish(gps_path);
  }
};

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GzWaypointBridge>());
  rclcpp::shutdown();
  return 0;
}
