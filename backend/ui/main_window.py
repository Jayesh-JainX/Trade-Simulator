from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
)
import sys

class TradeSimulatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trade Simulator")
        self.setGeometry(100, 100, 800, 600)
        self.simulator = None
        self.simulation_running = False

        main_layout = QHBoxLayout()

        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Input Parameters"))

        self.exchange_label = QLabel("Exchange: OKX")
        self.asset_input = QLineEdit("BTC-USDT")
        self.order_type_label = QLabel("Order Type: Market")
        self.quantity_input = QLineEdit("100")
        self.volatility_input = QLineEdit("0.02")
        self.fee_tier_input = QLineEdit("Tier1")
        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self.start_simulation)

        left_panel.addWidget(self.exchange_label)
        left_panel.addWidget(QLabel("Spot Asset:"))
        left_panel.addWidget(self.asset_input)
        left_panel.addWidget(self.order_type_label)
        left_panel.addWidget(QLabel("Quantity (USD):"))
        left_panel.addWidget(self.quantity_input)
        left_panel.addWidget(QLabel("Volatility:"))
        left_panel.addWidget(self.volatility_input)
        left_panel.addWidget(QLabel("Fee Tier:"))
        left_panel.addWidget(self.fee_tier_input)
        left_panel.addWidget(self.start_button)

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Output Parameters"))

        self.slippage_label = QLabel("Expected Slippage: N/A")
        self.fees_label = QLabel("Expected Fees: N/A")
        self.impact_label = QLabel("Market Impact: N/A")
        self.net_cost_label = QLabel("Net Cost: N/A")
        self.proportion_label = QLabel("Maker/Taker Proportion: N/A")
        self.latency_label = QLabel("Internal Latency: N/A")

        right_panel.addWidget(self.slippage_label)
        right_panel.addWidget(self.fees_label)
        right_panel.addWidget(self.impact_label)
        right_panel.addWidget(self.net_cost_label)
        right_panel.addWidget(self.proportion_label)
        right_panel.addWidget(self.latency_label)

        main_layout.addLayout(left_panel)
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        main_layout.addWidget(line)
        main_layout.addLayout(right_panel)

        self.setLayout(main_layout)

    def start_simulation(self):
        if not self.simulation_running:
            self.start_button.setText("Stop Simulation")
            self.simulation_running = True
            self.slippage_label.setText("Expected Slippage: Connecting...")
            self.fees_label.setText("Expected Fees: Connecting...")
            self.impact_label.setText("Market Impact: Connecting...")
            self.net_cost_label.setText("Net Cost: Connecting...")
            self.proportion_label.setText("Maker/Taker Proportion: Connecting...")
            self.latency_label.setText("Internal Latency: Connecting...")
            # Simulator will be created and started in main.py
        else:
            self.start_button.setText("Start Simulation")
            self.simulation_running = False
            if self.simulator:
                self.simulator.running = False

    def update_output(self, slippage, fees, impact, net_cost, proportion, latency):
        try:
            self.slippage_label.setText(f"Expected Slippage: {slippage}")
            self.fees_label.setText(f"Expected Fees: {fees}")
            self.impact_label.setText(f"Market Impact: {impact}")
            self.net_cost_label.setText(f"Net Cost: {net_cost}")
            self.proportion_label.setText(f"Maker/Taker Proportion: {proportion}")
            self.latency_label.setText(f"Internal Latency: {latency}")
            QApplication.processEvents()
        except Exception as e:
            logger.error(f"Error updating UI: {e}")
            self.simulation_running = False
            self.start_button.setText("Start Simulation")

def start_ui():
    app = QApplication(sys.argv)
    window = TradeSimulatorUI()
    window.show()
    sys.exit(app.exec_())
