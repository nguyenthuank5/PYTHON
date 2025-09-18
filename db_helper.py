# db_helper.py
from PyQt5.QtWidgets import QMessageBox
import pyodbc

SERVER = 'DESKTOP-614QJ3T\\SQLEXPRESS' # Tên localhost
DATABASE = 'DOAN' # Tên Database
DRIVER = '{SQL Server}'
TRUSTED_CONNECTION = 'Yes'

def connect_db():
    """Kết nối đến database SQL Server."""
    conn_str = (
        f'DRIVER={DRIVER};'
        f'SERVER={SERVER};'
        f'DATABASE={DATABASE};'
        f'TRUSTED_CONNECTION={TRUSTED_CONNECTION};'
    )
    try:
        cnxn = pyodbc.connect(conn_str)
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Lỗi kết nối database: {sqlstate}")
        return None

def execute_query(query, params=None, fetch=False, commit=False):
    """Thực thi truy vấn SQL và xử lý lỗi."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            if commit:
                conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi truy vấn: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

def search_food_names(keyword):
    """Tìm kiếm tên món ăn dựa trên từ khóa."""
    query = 'SELECT SoLuongTon FROM MonAn WHERE TenMon LIKE ?'
    result = execute_query(query, f'%{keyword}%', fetch=True)
    return result if result is not False else []

def update_food(food_name, quantity=1):
    """Cập nhật số lượng tồn của món ăn."""
    result = search_food_names(food_name)
    if result and result[0][0] > 0:
        query = 'UPDATE MonAn SET SoLuongTon = SoLuongTon - ? WHERE TenMon = ?'
        execute_query(query, (quantity, food_name), commit=True)
        print(f"Đã cập nhật số lượng cho {food_name}: Giảm {quantity}")    
        return True
    return False



def get_ingredient_quantity(ig_name):
    """Lấy số lượng tồn kho hiện tại của một nguyên liệu."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = 'SELECT SoLuongTonKho FROM NguyenLieuTonKho WHERE TenNguyenLieu = ?'
        cursor.execute(query, (ig_name,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]  # Lấy giá trị đầu tiên (số lượng tồn kho) từ Row
        else:
            return 0
    except Exception as e:
        print(f"Lỗi khi lấy số lượng tồn kho của {ig_name}: {e}")
        return -1

def update_ig(quantity_to_reduce, ig_name):
    """Cập nhật số lượng tồn kho của nguyên liệu và kiểm tra số lượng."""
    current_quantity = get_ingredient_quantity(ig_name)

    if current_quantity == -1:
        return False
    if current_quantity >= quantity_to_reduce:
        query = 'UPDATE NguyenLieuTonKho SET SoLuongTonKho = SoLuongTonKho - ? WHERE TenNguyenLieu = ?'
        success = execute_query(query, (quantity_to_reduce, ig_name), commit=True)
        if success:
            print(f"Đã cập nhật số lượng tồn của {ig_name}: Giảm {quantity_to_reduce}")
            return True
        return False

FOOD_INGREDIENTS = {
    "Gà rán truyền thống": {"Đùi gà": 150, "Bột chiên": 30, "Gia vị": 5},
    "Gà rán cay": {"Ức gà": 150, "Bột chiên cay": 30, "Gia vị": 5},
    "Gà nướng BBQ": {"Đùi gà": 180, "Sốt BBQ": 30},
    "Gà không xương": {"Thịt gà xay": 120, "Bột chiên": 30},
    "Gà viên": {"Thịt gà xay": 100, "Bột chiên xù": 25},
    "Gà sốt mật ong": {"Cánh gà": 150, "Sốt mật ong": 25},
    "Hamburger gà": {"Bánh mì burger": 1, "Ức gà": 100, "Xà lách": 20},
    "Hamburger gà cay": {"Bánh mì burger": 1, "Ức gà": 100, "Tương ớt": 20},
    "Hamburger phô mai": {"Bánh mì burger": 1, "Ức gà": 100, "Phô mai": 25},
    "Hamburger gà nướng": {"Bánh mì burger": 1, "Ức gà": 100, "Sốt BBQ": 20},
    "Bánh mì gà chiên": {"Bánh mì": 1, "Ức gà": 100, "Dưa leo": 30},
    "Khoai tây chiên vừa": {"Khoai tây": 150, "Dầu chiên": 20},
    "Khoai tây chiên lớn": {"Khoai tây": 200, "Dầu chiên": 30},
    "Khoai lắc phô mai": {"Khoai tây": 150, "Bột phô mai": 10},
    "Khoai chiên trứng muối": {"Khoai tây": 150, "Bột trứng muối": 10},
    "Gà rán phủ sốt phô mai": {"Ức gà": 150, "Bột chiên": 30, "Sốt phô mai": 30},
    "Gà viên phô mai": {"Thịt gà xay": 120, "Phô mai": 20},
    "Gà popcorn": {"Thịt gà xay": 100, "Bột chiên giòn": 30, "Gia vị": 5},
    "Wrap gà chiên": {"Bánh tortilla": 1, "Ức gà": 100, "Xà lách": 20},
    "Salad gà sốt mè rang": {"Ức gà": 100, "Xà lách": 50, "Sốt mè rang": 20},
    "Combo 1": {"Đùi gà": 150, "Bột chiên": 30, "Gia vị": 5, "Khoai tây": 150, "Dầu chiên": 20, "Pepsi": 1},
    "Combo 2": {"Thịt gà xay": 100, "Bột chiên xù": 25, "Khoai tây": 200, "Dầu chiên": 30, "Cocacola": 1},
    "Combo 3": {"Bánh mì burger": 1, "Ức gà": 100, "Xà lách": 20, "Khoai tây": 150, "Dầu chiên": 20, "7 Up": 1},
    "Combo 4": {"Ức gà": 150, "Bột chiên cay": 30, "Gia vị": 5, "Khoai tây": 150, "Bột phô mai": 10, "Pepsi": 1},
    "Combo 5": {"Đùi gà": 180, "Sốt BBQ": 30, "Bánh mì burger": 1, "Ức gà": 100, "Phô mai": 25, "Cocacola": 1}
}

COMBO_DRINKS_MAPPING = {
    "Combo 1": "Pepsi",
    "Combo 2": "Cocacola",
    "Combo 3": "7 Up",
    "Combo 4": "Pepsi",
    "Combo 5": "Cocacola"
}

# Định nghĩa stylesheet cho QMessageBox ở ngoài hàm
ERROR_MESSAGE_STYLE = """
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

def show_error_message(text):
    """Hiển thị hộp thoại thông báo lỗi."""
    msg = QMessageBox()
    msg.setWindowTitle("Thông báo")
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setStyleSheet(ERROR_MESSAGE_STYLE)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def update_combo(name):
    """Cập nhật số lượng tồn kho khi bán một món gà."""
    if not name:
        print("Tên món ăn không được để trống.")
        return False

    if name not in FOOD_INGREDIENTS:
        return False

    ingredients = FOOD_INGREDIENTS[name]
    for ingredient_name, quantity in ingredients.items():
        if name in COMBO_DRINKS_MAPPING and ingredient_name == COMBO_DRINKS_MAPPING[name] and quantity == 1:
            if not update_food(ingredient_name):
                return f"Không thể cập nhật món '{name}' do thiếu đồ uống '{ingredient_name}'."
        elif not update_ig(quantity, ingredient_name):
            return f"Không thể cập nhật món '{name}' do thiếu nguyên liệu '{ingredient_name}'."

    # print(f"Đã cập nhật nguyên liệu cho món '{name}'.")
    return True