import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64
from std_srvs.srv import Empty 

class VtolSpyNode(Node):
    def __init__(self):
        super().__init__('vtol_spy_node')
        
        self.publisher_ = self.create_publisher(Int64, 'nf_tracker', 10)
        self.timer = self.create_timer(0.42, self.timer_callback) # 420ms delay
        self.subscription = self.create_subscription(Int64, 'nf_tracker', self.listener_callback, 10)

        self.srv = self.create_service(Empty, 'land_drone', self.land_drone_callback)
        
        self.client = self.create_client(Empty, 'land_drone')

        self.counter = 0
        self.palindromic_events = 0
        self.nf_appearances = 0

    def timer_callback(self):
        msg = Int64()
        msg.data = self.counter
        self.publisher_.publish(msg)
        self.counter += 1

    def listener_callback(self, msg):
        val_str = str(msg.data)
        if val_str == val_str[::-1]:
            self.palindromic_events += 1
            
            if self.palindromic_events % 67 == 0:
                self.nf_appearances += 1
                self.get_logger().warn(f'Mas NF spotted! Appearance count: {self.nf_appearances}')
                
                if self.nf_appearances == 10:
                    self.call_landing_service()

    def land_drone_callback(self, request, response):
        self.get_logger().error('SERVICE SIGNAL RECEIVED: Drone is landing safely!')
        return response

    def call_landing_service(self):
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')
        
        req = Empty.Request()
        self.client.call_async(req)
        self.get_logger().info('Landing request sent to Mas NF rescue team!')

def main(args=None):
    rclpy.init(args=args)
    node = VtolSpyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()