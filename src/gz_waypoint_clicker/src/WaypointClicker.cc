#include <gz/gui/GuiEvents.hh>
#include <gz/gui/Plugin.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/vector3d.pb.h>

#include <QEvent>
#include <QObject>
#include <iostream>
#include <cmath>

namespace waypoint_clicker
{
class WaypointClicker : public gz::gui::Plugin
{
  Q_OBJECT

public:
  WaypointClicker()
  {
    std::cout << "[WaypointClicker] Plugin constructed" << std::endl;
  }

  void LoadConfig(const tinyxml2::XMLElement *) override
  {
    std::cout << "[WaypointClicker] Plugin loaded" << std::endl;
    qApp->installEventFilter(this);

    this->pub = this->node.Advertise<gz::msgs::Vector3d>(
      "/asv/gz_clicked_waypoint"
    );

    std::cout << "[WaypointClicker] Publishing clicks on /asv/gz_clicked_waypoint" << std::endl;
  }

protected:
  bool eventFilter(QObject *_obj, QEvent *_event) override
  {
    if (_event->type() == gz::gui::events::LeftClickToScene::kType)
    {
      auto clickEvent =
        static_cast<gz::gui::events::LeftClickToScene *>(_event);

      auto pos = clickEvent->Point();

      double x = pos.X();
      double y = pos.Y();
      double z = pos.Z();

      std::cout << "[WaypointClicker] Clicked scene point: "
                << "X=" << x
                << " Y=" << y
                << " Z=" << z
                << std::endl;

      

      gz::msgs::Vector3d msg;
      msg.set_x(x);
      msg.set_y(y);
      msg.set_z(z);

      this->pub.Publish(msg);

      std::cout << "[WaypointClicker] Published waypoint click: "
                << "X=" << x
                << " Y=" << y
                << " Z=" << z
                << std::endl;

      return false;
    }

    return QObject::eventFilter(_obj, _event);
  }

private:
  gz::transport::Node node;
  gz::transport::Node::Publisher pub;
};
}

GZ_ADD_PLUGIN(
  waypoint_clicker::WaypointClicker,
  gz::gui::Plugin
)

#include "WaypointClicker.moc"
