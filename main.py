from PyQt5 import QtWidgets, QtCore
from page_1 import Ui_Dialog as Page1UI
from page_2 import Ui_Dialog as Page2UI
from page_3 import Ui_Dialog as Page3UI
from page_4 import Ui_Dialog as Page4UI
from man_hinh_chinh import Ui_Dialog as Page0UI
from gio_hang import Ui_Dialog as Page5UI
from best_seller import Ui_Dialog as Pagebest
from chuyen_khoan import Ui_Dialog as CreditCart
import db_helper as db

from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QLabel, QWidget, QHBoxLayout
from PyQt5.QtGui import QFont
import unicodedata
import sys

def normalize_text(text):
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        return text.lower()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng dụng đặt món ăn tại bàn")
        self.resize(1220, 800)
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)
        self.scroll_area = None  # giữ lại scroll_area để tái sử dụng
        self.pages = []
        self.list_name_food = [] # List tên món ăn
        self.list_price = [] # List giá của món ăn
        self.buttons = {} # Lưu trữ các button sẽ xoá
        self.confirmed_items = set()
        for PageUI in [Page0UI, Page1UI, Page2UI, Page3UI, Page4UI, Page5UI, Pagebest, CreditCart]:
            widget = QtWidgets.QWidget()
            ui = PageUI()
            ui.setupUi(widget)
            self.stackedWidget.addWidget(widget)
            self.pages.append((widget, ui))

        self.build_food_index()  # Xây map từ tên món -> (page, tên, ảnh, nút)
        self.setup_navigation()
        self.setup_search()
    def setup_navigation(self):
        # Trang màn hình chính
        _, ui0 = self.pages[0]
        ui0.mon_an.clicked.connect(lambda: self.animate_page_change(1))  # Bấm menu từ màn hình chính -> page1
        ui0.gio_hang.clicked.connect(lambda: self.get_cart_page())  # Bấm giỏ hàng từ màn hình chính -> gape5
        # Trang 1
        _, ui1 = self.pages[1]
        ui1.page2.clicked.connect(lambda: self.animate_page_change(2))          # Chuyển đến trang 2
        ui1.page3.clicked.connect(lambda: self.animate_page_change(3))          # Chuyển đến trang 3
        ui1.page4.clicked.connect(lambda: self.animate_page_change(4))          # Chuyển đến giỏ hàng
        ui1.gio_hang.clicked.connect(lambda: self.get_cart_page())       # Chuyển đến giỏ hàng
        ui1.mon_an.clicked.connect(self.reset_all_pages)                        # Nhấn menu để thoát khỏi hàm tìm kiếm
        ui1.best_seller.clicked.connect(lambda: self.animate_page_change(6))    # Di chuyển đến trang best seller
        ui1.ga_ran_truyen_thong_35k.clicked.connect(lambda: self.add_to_cart("Gà rán truyền thống", 35))
        ui1.ga_ran_cay_38k.clicked.connect(lambda: self.add_to_cart("Gà rán cay", 38))
        ui1.ga_nuong_bbq_42k.clicked.connect(lambda: self.add_to_cart("Gà nướng BBQ", 42))
        ui1.ga_sot_mat_ong_40k.clicked.connect(lambda: self.add_to_cart("Gà sốt mật ong", 40))
        ui1.ga_khong_xuong_32k.clicked.connect(lambda: self.add_to_cart("Gà không xương", 32))
        ui1.ga_vien_30k.clicked.connect(lambda: self.add_to_cart("Gà viên", 30))
        ui1.hamburger_ga_40k.clicked.connect(lambda: self.add_to_cart("Hamburger gà", 40))
        ui1.hamburger_ga_cay_42k.clicked.connect(lambda: self.add_to_cart("Hamburger gà cay", 42))
        # Trang 2
        _, ui2 = self.pages[2]
        ui2.page1.clicked.connect(lambda: self.animate_page_change(1))
        ui2.page3.clicked.connect(lambda: self.animate_page_change(3))
        ui2.page4.clicked.connect(lambda: self.animate_page_change(4))
        ui2.gio_hang.clicked.connect(lambda: self.get_cart_page())
        ui2.mon_an.clicked.connect(self.reset_all_pages)
        ui2.best_seller.clicked.connect(lambda: self.animate_page_change(6))
        ui2.hamburger_pho_mai_45k.clicked.connect(lambda: self.add_to_cart("Hamburger phô mai", 45))
        ui2.khoai_lac_pho_mai_25k.clicked.connect(lambda: self.add_to_cart("Khoai lắc phô mai", 25))
        ui2.khoai_chien_trung_muoi_27k.clicked.connect(lambda: self.add_to_cart("Khoai chiên trứng muối", 27))
        ui2.hamburger_ga_nuong_44k.clicked.connect(lambda: self.add_to_cart("Hamburger gà nướng", 44))
        ui2.khoai_tay_chien_lon_28k.clicked.connect(lambda: self.add_to_cart("Khoai tây chiên lớn", 28))
        ui2.banh_mi_ga_chien_30k.clicked.connect(lambda: self.add_to_cart("Bánh mì gà chiên", 30))
        ui2.ga_ran_phu_sot_pho_mai_45k.clicked.connect(lambda: self.add_to_cart("Gà rán phủ sốt phô mai", 45))
        ui2.khoai_tay_chien_vua_20k.clicked.connect(lambda: self.add_to_cart("Khoai tây chiên vừa", 20))
        # Trang 3
        _, ui3 = self.pages[3]
        ui3.page1.clicked.connect(lambda: self.animate_page_change(1))
        ui3.page2.clicked.connect(lambda: self.animate_page_change(2))
        ui3.page4.clicked.connect(lambda: self.animate_page_change(4))
        ui3.gio_hang.clicked.connect(lambda: self.get_cart_page())
        ui3.mon_an.clicked.connect(self.reset_all_pages)
        ui3.best_seller.clicked.connect(lambda: self.animate_page_change(6))
        ui3.ga_vien_pho_mai_35k.clicked.connect(lambda: self.add_to_cart("Gà viên phô mai", 35))
        ui3.combo1.clicked.connect(lambda: self.add_to_cart("Combo 1", 59))
        ui3.combo2.clicked.connect(lambda: self.add_to_cart("Combo 2", 58))
        ui3.combo3.clicked.connect(lambda: self.add_to_cart("Combo 3", 60))
        ui3.combo4.clicked.connect(lambda: self.add_to_cart("Combo 4", 62))
        ui3.salad_ga_sot_me_rang_38k.clicked.connect(lambda: self.add_to_cart("Salad gà sốt mè rang", 38))
        ui3.ga_popcorn_32k.clicked.connect(lambda: self.add_to_cart("Gà Popcorn", 32))
        ui3.warp_ga_chien_40k.clicked.connect(lambda: self.add_to_cart("Wrap gà chiên", 40))
        
        # Trang 4
        _, ui4 = self.pages[4]
        ui4.page1.clicked.connect(lambda: self.animate_page_change(1))
        ui4.page2.clicked.connect(lambda: self.animate_page_change(2))
        ui4.page3.clicked.connect(lambda: self.animate_page_change(3))
        ui4.gio_hang.clicked.connect(lambda: self.get_cart_page())
        ui4.mon_an.clicked.connect(self.reset_all_pages)
        ui4.best_seller.clicked.connect(lambda: self.animate_page_change(6))
        ui4.combo5.clicked.connect(lambda: self.add_to_cart("Combo 5", 75))
        ui4.pepsi_12k.clicked.connect(lambda: self.add_to_cart("Pepsi", 12))
        ui4.coca_12k.clicked.connect(lambda: self.add_to_cart("Cocacola", 12))
        ui4.up_12k.clicked.connect(lambda: self.add_to_cart("7 Up", 12))
        ui4.mirinda_12k.clicked.connect(lambda: self.add_to_cart("Mirinda", 12))
        ui4.tra_lipton_15k.clicked.connect(lambda: self.add_to_cart("Trà Lipton", 15))
        ui4.nuoc_loc_10k.clicked.connect(lambda: self.add_to_cart("Nước suối", 10))
        ui4.sua_milo_15k.clicked.connect(lambda: self.add_to_cart("Sữa Milo", 15))
        # Trang giỏ hàng
        _, ui5 = self.pages[5]
        ui5.mon_an.clicked.connect(lambda: self.animate_page_change(1))
        ui5.xac_nhan.clicked.connect(lambda: self.confirm_cancel())  # Đảm bảo nút được kích hoạt khi bắt đầu
        # Trang best seller
        _, ui6 = self.pages[6]
        ui6.mon_an.clicked.connect(lambda: self.animate_page_change(1))
        ui6.gio_hang.clicked.connect(lambda: self.get_cart_page())
        ui6.ga_ran_cay_38k.clicked.connect(lambda: self.add_to_cart("Gà rán cay", 38))
        ui6.ga_sot_mat_ong_40k.clicked.connect(lambda: self.add_to_cart("Gà sốt mật ong", 40))
        ui6.hamburger_pho_mai_45k.clicked.connect(lambda: self.add_to_cart("Hamburger phô mai", 45))
        ui6.khoai_lac_pho_mai_25k.clicked.connect(lambda: self.add_to_cart("Khoai lắc phô mai", 25))
        ui6.warp_ga_chien_40k.clicked.connect(lambda: self.add_to_cart("Wrap gà chiên", 40))
        ui6.ga_ran_phu_sot_pho_mai_45k.clicked.connect(lambda: self.add_to_cart("Gà rán phủ sốt phô mai", 45))
        # Trang chuyển khoản 
        _, ui7 = self.pages[7]
        ui7.xac_nhan_thanh_toan.clicked.connect(lambda: self.reset_cart_page()) # Xác nhận sẽ chuyển về trang đầu
        ui7.gio_hang.clicked.connect(lambda: self.animate_page_change(5))
    def setup_search(self):
        for widget, ui in self.pages:
            if hasattr(ui, "tim_kiem"):
                ui.tim_kiem.returnPressed.connect(self.handle_exact_search)

    def build_food_index(self):
    # Tạo từ điển: ten_mon_an -> (page_index, label_ten, label_anh, button_them, (geometry_ten, geometry_anh, geometry_button))
        self.food_index = {}

    # Page 1
        _, ui1 = self.pages[1]
        self.food_index.update({
        "gà rán truyền thống": (1, ui1.label_58, ui1.label_56, ui1.ga_ran_truyen_thong_35k,
                                (ui1.label_58.geometry(), ui1.label_56.geometry(), ui1.ga_ran_truyen_thong_35k.geometry())),
        "gà rán cay": (1, ui1.label_60, ui1.label_57, ui1.ga_ran_cay_38k,
                       (ui1.label_60.geometry(), ui1.label_57.geometry(), ui1.ga_ran_cay_38k.geometry())),
        "gà nướng bbq": (1, ui1.label_32, ui1.label_59, ui1.ga_nuong_bbq_42k,
                         (ui1.label_32.geometry(), ui1.label_59.geometry(), ui1.ga_nuong_bbq_42k.geometry())),
        "gà sốt mật ong": (1, ui1.label_33, ui1.label_61, ui1.ga_sot_mat_ong_40k,
                           (ui1.label_33.geometry(), ui1.label_61.geometry(), ui1.ga_sot_mat_ong_40k.geometry())),
        "gà không xương": (1, ui1.label_63, ui1.label_62, ui1.ga_khong_xuong_32k,
                           (ui1.label_63.geometry(), ui1.label_62.geometry(), ui1.ga_khong_xuong_32k.geometry())),
        "gà viên": (1, ui1.label_66, ui1.label_65, ui1.ga_vien_30k,
                    (ui1.label_66.geometry(), ui1.label_65.geometry(), ui1.ga_vien_30k.geometry())),
        "hamburger gà": (1, ui1.label_34, ui1.label_64, ui1.hamburger_ga_40k,
                         (ui1.label_34.geometry(), ui1.label_64.geometry(), ui1.hamburger_ga_40k.geometry())),
        "hamburger gà cay": (1, ui1.label_35, ui1.label_67, ui1.hamburger_ga_cay_42k,
                             (ui1.label_35.geometry(), ui1.label_67.geometry(), ui1.hamburger_ga_cay_42k.geometry())),
    })

    # Page 2
        _, ui2 = self.pages[2]
        self.food_index.update({
        "hamburger phô mai": (2, ui2.label_58, ui2.label_56, ui2.hamburger_pho_mai_45k,
                              (ui2.label_58.geometry(), ui2.label_56.geometry(), ui2.hamburger_pho_mai_45k.geometry())),
        "khoai lắc phô mai": (2, ui2.label_33, ui2.label_61, ui2.khoai_lac_pho_mai_25k,
                              (ui2.label_33.geometry(), ui2.label_61.geometry(), ui2.khoai_lac_pho_mai_25k.geometry())),
        "khoai chiên trứng muối": (2, ui2.label_34, ui2.label_64, ui2.khoai_chien_trung_muoi_27k,
                                   (ui2.label_34.geometry(), ui2.label_64.geometry(), ui2.khoai_chien_trung_muoi_27k.geometry())),
        "khoai tây chiên vừa": (2, ui2.label_66, ui2.label_65, ui2.khoai_tay_chien_vua_20k,
                                (ui2.label_66.geometry(), ui2.label_65.geometry(), ui2.khoai_tay_chien_vua_20k.geometry())),
        "hamburger gà nướng": (2, ui2.label_60, ui2.label_57, ui2.hamburger_ga_nuong_44k,
                               (ui2.label_60.geometry(), ui2.label_57.geometry(), ui2.hamburger_ga_nuong_44k.geometry())),
        "khoai tây chiên lớn": (2, ui2.label_32, ui2.label_59, ui2.khoai_tay_chien_lon_28k,
                                (ui2.label_32.geometry(), ui2.label_59.geometry(), ui2.khoai_tay_chien_lon_28k.geometry())),
        "bánh mì gà chiên": (2, ui2.label_63, ui2.label_62, ui2.banh_mi_ga_chien_30k,
                             (ui2.label_63.geometry(), ui2.label_62.geometry(), ui2.banh_mi_ga_chien_30k.geometry())),
        "gà rán phủ sốt phô mai": (2, ui2.label_35, ui2.label_67, ui2.ga_ran_phu_sot_pho_mai_45k,
                                  (ui2.label_35.geometry(), ui2.label_67.geometry(), ui2.ga_ran_phu_sot_pho_mai_45k.geometry())),
    })

    # Page 3
        _, ui3 = self.pages[3]
        self.food_index.update({
        "gà viên phô mai": (3, ui3.label_58, ui3.label_56, ui3.ga_vien_pho_mai_35k,
                            (ui3.label_58.geometry(), ui3.label_56.geometry(), ui3.ga_vien_pho_mai_35k.geometry())),
        "combo 1": (3, ui3.label_32, ui3.label_59, ui3.combo1,
                    (ui3.label_32.geometry(), ui3.label_59.geometry(), ui3.combo1.geometry())),
        "combo 2": (3, ui3.label_33, ui3.label_61, ui3.combo2,
                    (ui3.label_33.geometry(), ui3.label_61.geometry(), ui3.combo2.geometry())),
        "combo 3": (3, ui3.label_34, ui3.label_64, ui3.combo3,
                    (ui3.label_34.geometry(), ui3.label_64.geometry(), ui3.combo3.geometry())),
        "combo 4": (3, ui3.label_35, ui3.label_67, ui3.combo4,
                    (ui3.label_35.geometry(), ui3.label_67.geometry(), ui3.combo4.geometry())),
        "salad gà sốt mè rang": (3, ui3.label_66, ui3.label_65, ui3.salad_ga_sot_me_rang_38k,
                                 (ui3.label_66.geometry(), ui3.label_65.geometry(), ui3.salad_ga_sot_me_rang_38k.geometry())),
        "gà popcorn": (3, ui3.label_60, ui3.label_57, ui3.ga_popcorn_32k,
                       (ui3.label_60.geometry(), ui3.label_57.geometry(), ui3.ga_popcorn_32k.geometry())),
        "wrap gà chiên": (3, ui3.label_63, ui3.label_62, ui3.warp_ga_chien_40k,
                          (ui3.label_63.geometry(), ui3.label_62.geometry(), ui3.warp_ga_chien_40k.geometry())),
    })

    # Page 4
        _, ui4 = self.pages[4] 
        self.food_index.update({
        "combo 5": (4, ui4.label_58, ui4.label_56, ui4.combo5,
                    (ui4.label_58.geometry(), ui4.label_56.geometry(), ui4.combo5.geometry())),
        "pepsi": (4, ui4.label_60, ui4.label_57, ui4.pepsi_12k,
                    (ui4.label_60.geometry(), ui4.label_57.geometry(), ui4.pepsi_12k.geometry())),
        "coca cola": (4, ui4.label_63, ui4.label_62, ui4.coca_12k,
                    (ui4.label_63.geometry(), ui4.label_62.geometry(), ui4.coca_12k.geometry())),
        "7 up": (4, ui4.label_66, ui4.label_65, ui4.up_12k,
                    (ui4.label_66.geometry(), ui4.label_65.geometry(), ui4.up_12k.geometry())),
        "mirinda": (4, ui4.label_32, ui4.label_59, ui4.mirinda_12k,
                    (ui4.label_32.geometry(), ui4.label_59.geometry(), ui4.mirinda_12k.geometry())),
        "trà lipton": (4, ui4.label_33, ui4.label_61, ui4.tra_lipton_15k,
                    (ui4.label_33.geometry(), ui4.label_61.geometry(), ui4.tra_lipton_15k.geometry())),
        "sữa milo": (4, ui4.label_34, ui4.label_64, ui4.sua_milo_15k,
                    (ui4.label_34.geometry(), ui4.label_64.geometry(), ui4.sua_milo_15k.geometry())),
        "nước lọc": (4, ui4.label_35, ui4.label_67, ui4.nuoc_loc_10k,
                    (ui4.label_35.geometry(), ui4.label_67.geometry(), ui4.nuoc_loc_10k.geometry())),    
    })
    
    

    def handle_exact_search(self):
        keyword = ""
        for _, ui in self.pages:
            if hasattr(ui, "tim_kiem") and ui.tim_kiem.hasFocus():
                keyword = normalize_text(ui.tim_kiem.text().strip())
                break

        # Tìm kiếm không dấu, không phân biệt hoa thường
        matched_item = None
        for food_name, value in self.food_index.items():
            if normalize_text(food_name) == keyword:
                matched_item = (food_name, *value)
                break

        if matched_item:
            _, page_idx, name_lbl, img_lbl, btn, _ = matched_item

            self.stackedWidget.setCurrentIndex(page_idx)

            # Ẩn toàn bộ món ăn khác
            for food_name, (p, n_lbl, i_lbl, b_btn, _) in self.food_index.items():
                if p == page_idx:
                    n_lbl.hide()
                    i_lbl.hide()
                    b_btn.hide()

            # Hiện đúng món cần tìm
            name_lbl.show()
            img_lbl.show()
            btn.show()

            # Đẩy món cần tìm lên đầu
            img_lbl.move(290, 430)
            name_lbl.move(280, 260)
            btn.move(420, 440)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Không tìm thấy")
            msg.setIcon(QMessageBox.Information)
            msg.setText("Không tìm thấy món ăn này trong cơ sở dữ liệu.")

            # Tạo stylesheet cho QMessageBox
            stylesheet = """
            QMessageBox {
                background-color: #f0f8ff; /* AliceBlue */
            }

            QMessageBox QLabel {
                color: #2f4f4f; /* DarkSlateGray */
                font-size: 14px;
            }

            QMessageBox QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                min-width: 80px;
            }

            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
            """

            # Áp dụng stylesheet cho QMessageBox
            msg.setStyleSheet(stylesheet)

            # Thêm nút OK (nếu chưa có) và hiển thị
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    # Hiện lại toàn bộ món ăn trên 4 page
    
    def reset_all_pages(self):
        for name, (page_idx, name_lbl, img_lbl, btn, (g_name, g_img, g_btn)) in self.food_index.items():
            # Phục hồi lại đúng vị trí ban đầu
            name_lbl.setGeometry(g_name)
            img_lbl.setGeometry(g_img)
            btn.setGeometry(g_btn)

            # Hiện lại tất cả
            name_lbl.show()
            img_lbl.show()
            btn.show()


    def animate_page_change(self, next_index):
        next_widget = self.stackedWidget.widget(next_index)

        # Đưa trang mới lên
        self.stackedWidget.setCurrentWidget(next_widget)
        # Có thể loại bỏ hiệu ứng fade nếu không cần thiết
        # # Hiệu ứng fade mờ dần vào
        opacity_effect = QGraphicsOpacityEffect()
        next_widget.setGraphicsEffect(opacity_effect)
        self.fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)  
        self.fade_animation.setStartValue(0.0)  
        self.fade_animation.setEndValue(1.0)    
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)  
        
        # # Bắt đầu animation
        self.fade_animation.start()

    def update_cart_display(self, food, total_price):
        _, ui5 = self.pages[5]

        if hasattr(self, 'cart_widgets'):
            for lbl, btn in self.cart_widgets:
                lbl.deleteLater()
                if btn:
                    btn.deleteLater()

        self.cart_widgets = []

        # Thiết lập font
        font_total = QFont()
        font_total.setPointSize(12)
        font_total.setBold(True)
        ui5.label_9.setFont(font_total)
        ui5.label_9.setText(f"Tổng số tiền: {total_price}.000 VNĐ")

        font_items = QFont()
        font_items.setPointSize(14)
        font_items.setBold(True)
        ui5.label_7.setFont(font_items)
        ui5.label_7.setText("Giỏ hàng của bạn:")
        # ui5.label_7.hide()  # Ẩn label cũ

        # Nếu đã có scroll_area, xoá nội dung cũ
        if self.scroll_area:
            self.scroll_area.deleteLater()

        # Tạo scroll area
        self.scroll_area = QScrollArea(ui5.frame_gio_hang if hasattr(ui5, 'frame_gio_hang') else ui5.label_7.parent())
        self.scroll_area.setGeometry(600, 300, 550, 300)  # điều chỉnh vị trí và kích thước vùng scroll
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #ffe5b4; border: none; }")

        # Widget chứa nội dung
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #ffe5b4;")  # nâu nhạt
        layout = QVBoxLayout(content_widget)

        y_position = 10
        y_offset = 30
        for i in range(len(food)):
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)

            item_label = QLabel(f"{self.list_name_food[i]} - {self.list_price[i]}.000 VNĐ")
            item_label.setFont(font_items)
            item_label.setFixedWidth(350)  # Đặt chiều rộng cố định cho label

            button = QPushButton("Xoá")
            button.setFont(font_items)
            button.setFixedWidth(100)  # Đặt chiều rộng cố định cho button
            button.setFixedHeight(30) # Đặt chiều cao cố định cho button
            button.setStyleSheet("""
                QPushButton {
                    /* width: 25px; */ /* Không cần thiết khi dùng setFixedWidth */
                    /* height: 25px; */ /* Không cần thiết khi dùng setFixedHeight */
                    border-radius: 5px;
                    background-color: rgb(255,140,0);
                    color: black;
                }
                QPushButton:hover {
                    background-color: rgb(255, 170, 127);
                }
            """)

            if self.list_name_food[i] not in self.confirmed_items:
                item_layout.addWidget(item_label)
                item_layout.addWidget(button)
                layout.addWidget(item_widget)
                button.clicked.connect(lambda _, n=self.list_name_food[i], l=item_label, b=button: self.remove_from_cart(n, l, b))
                self.cart_widgets.append((item_label, button))
            else:
                item_layout.addWidget(item_label)
                layout.addWidget(item_widget)
                self.cart_widgets.append((item_label, None))

            y_position += y_offset + 10  # Tăng vị trí y cho item tiếp theo

        self.scroll_area.setWidget(content_widget)
        self.scroll_area.show()

    def reset_cart_page(self):
        # Đặt lại giỏ hàng về trạng thái ban đầu

        self.list_name_food.clear()
        self.list_price.clear()
        self.confirmed_items.clear()
        self.update_cart_display({}, 0)
        self.pages[5][1].mon_an.setEnabled(True)

        self.pages[5][1].label_7.setText("Chưa có món ăn được thêm:")
        self.pages[5][1].label_9.setText("Hiện giá tiền:")
        self.stackedWidget.setCurrentIndex(0)

        msg = QMessageBox()
        msg.setWindowTitle("Thông báo")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Đã xác nhận thanh toán. Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!")

        # Tạo stylesheet cho QMessageBox
        stylesheet = """
        QMessageBox {
            background-color: #f0f8ff; /* AliceBlue */
        }

        QMessageBox QLabel {
            color: #2f4f4f; /* DarkSlateGray */
            font-size: 14px;
        }

        QMessageBox QPushButton {
            background-color: #4CAF50; /* Red */
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 12px;
            min-width: 80px;
        }

        QMessageBox QPushButton:hover {
            background-color: #FF6961;
        }
        """
        msg.setStyleSheet(stylesheet)

        # Thêm nút OK (nếu chưa có) và hiển thị
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    def confirm_cancel(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Xác nhận thao tác")
        msgBox.setText("Bạn có chắc chắn muốn thực hiện thao tác này?")
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        msgBox.setStyleSheet( """
        QMessageBox {
            background-color: #f0f8ff;
        }
        QMessageBox QLabel {
            color: #2f4f4f;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 12px;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #45a049;
        }
        """)
        reply = msgBox.exec_()

        if reply == QMessageBox.Yes:
            self.perform_action()
        else:
            self.cancel_action()

    def perform_action(self):
        self.remove_all_delete_buttons()
        
    def cancel_action(self):
        msg = QMessageBox()
        msg.setWindowTitle("Thông báo")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Đã huỷ thao tác")

        # Style đẹp
        stylesheet = """
        QMessageBox {
            background-color: #f0f8ff;
        }
        QMessageBox QLabel {
            color: #2f4f4f;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 12px;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #45a049;
        }
        """
        msg.setStyleSheet(stylesheet)
        msg.exec_()

    def remove_all_delete_buttons(self):
        _, ui5 = self.pages[5]
        self.confirmed_items = set(self.list_name_food)
        update_success = False

        for food in self.confirmed_items:
            result = db.update_combo(food)
            if result:
                update_success = True
        if update_success:
            print("Thành công")

        msg = QMessageBox()
        msg.setWindowTitle("Thông báo")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Đã xác nhận món thành công")

        # Style đẹp
        stylesheet = """
        QMessageBox {
            background-color: #f0f8ff;
        }
        QMessageBox QLabel {
            color: #2f4f4f;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 12px;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #45a049;
        }
        """
        msg.setStyleSheet(stylesheet)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        # Hiện thông báo xác nhận thành công
        # 2) Ẩn tất cả nút Xóa hiện tại
        if hasattr(self, 'cart_widgets'):
            for label, button in self.cart_widgets:
                if button:
                    button.hide()
        ui5.mon_an.setEnabled(False)
        ui5.chuyen_khoan.clicked.connect(lambda: self.animate_page_change(7))
        ui5.tien_mat.clicked.connect(lambda: self.reset_cart_page())

    def add_to_cart(self, name, price):
        # Tạo một QMessageBox instance
        if not db.update_food(name):
            for food_name, (p, n_lbl, i_lbl, b_btn, _) in self.food_index.items():
                if name.lower() == food_name:
                    db.show_error_message("Món ăn này đã hết vui lòng chọn món khác")
                    b_btn.hide()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Thông báo")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"Đã thêm {name} vào giỏ hàng")

            # Tạo stylesheet cho QMessageBox
            stylesheet = """
            QMessageBox {
                background-color: #f0f8ff; /* AliceBlue */
            }

            QMessageBox QLabel {
                color: #2f4f4f; /* DarkSlateGray */
                font-size: 14px;
            }

            QMessageBox QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                min-width: 80px;
            }

            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
            """

            # Áp dụng stylesheet cho QMessageBox
            msg.setStyleSheet(stylesheet)
            # Thêm nút OK (nếu chưa có) và hiển thị
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self.list_name_food.append(name)
            self.list_price.append(price)
            print(f"Giỏ hàng: {self.list_name_food}, Tổng tiền: {sum(self.list_price)}")
            self.update_cart_display(self.list_name_food, sum(self.list_price))

        

    def remove_from_cart(self, name, label, button):
        # 1) Xoá label + button
        label.deleteLater()
        button.deleteLater()

        # 2) Xoá khỏi dữ liệu
        for i in range(len(self.list_name_food)):
            if name == self.list_name_food[i]:
                self.list_name_food.pop(i)
                self.list_price.pop(i)
                break
        msg = QMessageBox()
        msg.setWindowTitle("Thông báo")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Đã xoá {name} vào giỏ hàng")

        # Tạo stylesheet cho QMessageBox
        stylesheet = """
        QMessageBox {
            background-color: #f0f8ff; /* AliceBlue */
        }

        QMessageBox QLabel {
            color: #2f4f4f; /* DarkSlateGray */
            font-size: 14px;
        }

        QMessageBox QPushButton {
            background-color: #FF0000; /* Red */
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 12px;
            min-width: 80px;
        }

        QMessageBox QPushButton:hover {
            background-color: #FF6961;
        }
        """

        # Áp dụng stylesheet cho QMessageBox
        msg.setStyleSheet(stylesheet)

        # Thêm nút OK (nếu chưa có) và hiển thị
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        # 3) Cập nhật lại giỏ hàng (vẽ lại & xoá cũ)
        db.update_food(name, -1)
        total = sum(self.list_price)
        self.update_cart_display(self.list_name_food, total)

    def get_cart_page(self):
        # Chuyển đến trang giỏ hàng
        _, ui5 = self.pages[5]
        if ui5.label_7.text() == "Chưa có món ăn được thêm:" and ui5.label_9.text() == "Hiện giá tiền:":
            # QMessageBox.warning(self, "Giỏ hàng trống", "Giỏ hàng của bạn hiện tại chưa có món nào.")
            msg = QMessageBox()
            msg.setWindowTitle("Giỏ hàng trống")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"Giỏ hàng của bạn hiện tại chưa có món nào")

            # Tạo stylesheet cho QMessageBox
            stylesheet = """
            QMessageBox {
                background-color: #f0f8ff; /* AliceBlue */
            }

            QMessageBox QLabel {
                color: #2f4f4f; /* DarkSlateGray */
                font-size: 14px;
            }

            QMessageBox QPushButton {
                background-color: #FF0000; /* Red */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                min-width: 80px;
            }

            QMessageBox QPushButton:hover {
                background-color: #FF6961;
            }
            """


            # Áp dụng stylesheet cho QMessageBox
            msg.setStyleSheet(stylesheet)

            # Thêm nút OK (nếu chưa có) và hiển thị
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.stackedWidget.setCurrentIndex(5)
    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
