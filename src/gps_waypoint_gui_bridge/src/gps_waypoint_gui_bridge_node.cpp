#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/path.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>

#include <cmath>
#include <cstdlib>
#include <sstream>
#include <vector>
#include <utility>
#include <thread>

class GPSWaypointGUIBridge : public rclcpp::Node
{
public:
  GPSWaypointGUIBridge() : Node("gps_waypoint_gui_bridge_node")
  {
    origin_lat_ = -33.724223;
    origin_lon_ = 150.679736;

    waypoint_sub_ = this->create_subscription<nav_msgs::msg::Path>(
      "/asv/waypoints_gps",
      10,
      std::bind(&GPSWaypointGUIBridge::waypointGpsCallback, this, std::placeholders::_1)
    );

    local_path_pub_ = this->create_publisher<nav_msgs::msg::Path>(
      "/asv/waypoints",
      10
    );

    RCLCPP_INFO(this->get_logger(), "GPS Waypoint GUI Bridge started");
    RCLCPP_INFO(this->get_logger(), "Subscribing: /asv/waypoints_gps");
    RCLCPP_INFO(this->get_logger(), "Publishing: /asv/waypoints");
  }

private:
  double origin_lat_;
  double origin_lon_;

  rclcpp::Subscription<nav_msgs::msg::Path>::SharedPtr waypoint_sub_;
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr local_path_pub_;

  void latLonToXY(double lat, double lon, double &x, double &y)
  {
    double meters_per_deg_lat = 111320.0;
    double meters_per_deg_lon = 111320.0 * std::cos(origin_lat_ * M_PI / 180.0);

    x = (lon - origin_lon_) * meters_per_deg_lon;
    y = (lat - origin_lat_) * meters_per_deg_lat;
  }

  void waypointGpsCallback(const nav_msgs::msg::Path::SharedPtr msg)
  {
    if (msg->poses.empty())
    {
      RCLCPP_WARN(this->get_logger(), "Received empty /asv/waypoints_gps");
      return;
    }

    std::vector<std::pair<double, double>> local_waypoints;

    nav_msgs::msg::Path local_path;
    local_path.header.stamp = this->now();
    local_path.header.frame_id = "map";

    for (size_t i = 0; i < msg->poses.size(); i++)
    {
      double lat = msg->poses[i].pose.position.x;
      double lon = msg->poses[i].pose.position.y;

      double x = 0.0;
      double y = 0.0;

      latLonToXY(lat, lon, x, y);
      local_waypoints.push_back({x, y});

      geometry_msgs::msg::PoseStamped pose;
      pose.header.stamp = this->now();
      pose.header.frame_id = "map";
      pose.pose.position.x = x;
      pose.pose.position.y = y;
      pose.pose.position.z = 0.0;
      pose.pose.orientation.w = 1.0;

      local_path.poses.push_back(pose);

      RCLCPP_INFO(
        this->get_logger(),
        "GPS WP%ld: LAT=%.8f LON=%.8f -> X=%.2f Y=%.2f",
        static_cast<long>(i + 1),
        lat,
        lon,
        x,
        y
      );
    }

    local_path_pub_->publish(local_path);
    spawnWaypoints(local_waypoints);
  }

  void spawnWaypoints(const std::vector<std::pair<double, double>> &wps)
  {
    for (size_t i = 0; i < wps.size(); i++)
    {
      int wp_id = static_cast<int>(i + 1);
      double x = wps[i].first;
      double y = wps[i].second;

      std::thread([this, wp_id, x, y]() {
        this->spawnMarker(wp_id, x, y);
      }).detach();

      if (i > 0)
      {
        double x1 = wps[i - 1].first;
        double y1 = wps[i - 1].second;
        double x2 = wps[i].first;
        double y2 = wps[i].second;

        std::thread([this, wp_id, x1, y1, x2, y2]() {
          this->spawnConnector(wp_id, x1, y1, x2, y2);
        }).detach();
      }
    }
  }

  void spawnMarker(int wp_id, double x, double y)
  {
    std::stringstream ss;

    ss << "gz service -s /world/sydney_regatta/create "
       << "--reqtype gz.msgs.EntityFactory "
       << "--reptype gz.msgs.Boolean "
       << "--timeout 10000 "
       << "--req 'sdf:\"<sdf version=\\\"1.9\\\">"
       << "<model name=\\\"gps_gui_waypoint_marker_" << wp_id << "\\\">"
       << "<static>true</static>"
       << "<pose>" << x << " " << y << " 1.2 0 0 0</pose>"
       << "<link name=\\\"link\\\">"
       << "<visual name=\\\"gps_gui_waypoint_visual\\\">"
       << "<pose>0 0 0 1.5708 0 1.5708</pose>"
       << "<geometry><mesh>"
       << "<uri>file:///home/user/vrx_ws/src/vrx/vrx_gz/models/my_asv/meshes/map_waypoint_centered.STL</uri>"
       << "<scale>0.05 0.05 0.05</scale>"
       << "</mesh></geometry>"
       << "</visual>"
       << "</link>"
       << "</model>"
       << "</sdf>\", name:\"gps_gui_waypoint_marker_" << wp_id << "\"'";

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
       << "<model name=\\\"gps_gui_waypoint_connector_" << wp_id << "\\\">"
       << "<static>true</static>"
       << "<pose>" << mid_x << " " << mid_y << " 0.08 0 0 " << yaw << "</pose>"
       << "<link name=\\\"link\\\">"
       << "<visual name=\\\"red_connector_visual\\\">"
       << "<geometry><box>"
       << "<size>" << length << " 0.12 0.05</size>"
       << "</box></geometry>"
       << "<material>"
       << "<ambient>1 0 0 1</ambient>"
       << "<diffuse>1 0 0 1</diffuse>"
       << "<emissive>0.5 0 0 1</emissive>"
       << "</material>"
       << "</visual>"
       << "</link>"
       << "</model>"
       << "</sdf>\", name:\"gps_gui_waypoint_connector_" << wp_id << "\"'";

    std::system(ss.str().c_str());
  }
};

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GPSWaypointGUIBridge>());
  rclcpp::shutdown();
  return 0;
}
