import flet as ft
import qrcode
import base64
import os
import json
import re
from io import BytesIO
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from typing import Optional, Tuple, Dict, Any

class QRCodeGeneratorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.setup_colors()
        self.setup_constants()
        self.setup_app_settings()
        self.load_settings()
        self.setup_ui_elements()
        self.setup_event_handlers()
        
    def setup_page(self):
        """إعداد إعدادات الصفحة الأساسية"""
        self.page.title = "نظام توليد QR Code مشفر"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.rtl = True
        self.page.window_width = 1200
        self.page.window_height = 850
        self.page.padding = 0
        self.page.bgcolor = "#f0f4f8"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.window_maximizable = True
        self.page.window_maximized = False
        
    def setup_colors(self):
        """تعريف الألوان المستخدمة في التطبيق"""
        self.colors = {
            "primary": "#3b82f6",
            "secondary": "#0284c7",
            "accent": "#f97316",
            "text": "#1e293b",
            "success": "#10b981",
            "error": "#ef4444",
            "header_bg": "#1e40af",
            "card_bg": "white",
            "dark_bg": "#0f172a",
            "dark_header": "#1e3a8a"
        }
        
    def setup_constants(self):
        """إعداد الثوابت والمتغيرات المهمة"""
        self.is_desktop = True
        self.KEY_FILE = "encryption_key.bin"
        self.SETTINGS_FILE = "settings.json"
        self.load_or_generate_key()
        
    def load_or_generate_key(self):
        """تحميل مفتاح التشفير من ملف أو توليد مفتاح جديد"""
        try:
            if os.path.exists(self.KEY_FILE):
                with open(self.KEY_FILE, 'rb') as f:
                    self.KEY = f.read()
            else:
                self.KEY = get_random_bytes(32)  # استخدام 256-bit key بدلاً من 128-bit
                with open(self.KEY_FILE, 'wb') as f:
                    f.write(self.KEY)
        except Exception as e:
            print(f"Error handling encryption key: {str(e)}")
            self.KEY = get_random_bytes(32)
            
    def setup_app_settings(self):
        """إعداد الإعدادات الافتراضية للتطبيق"""
        self.app_settings = {
            "save_path": os.path.join(os.path.expanduser("~"), "QR-pass"),
            "auto_save": False,
            "image_quality": "عالية",
            "qr_size": "متوسط",
            "qr_color": "#000000",
            "qr_bg_color": "#FFFFFF",
            "language": "ar"
        }
        
    def load_settings(self):
        """تحميل الإعدادات من ملف"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # التحقق من صحة المسار قبل التحميل
                    if 'save_path' in loaded_settings and self.validate_path(loaded_settings['save_path']):
                        self.app_settings.update(loaded_settings)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            print(f"Error loading settings: {str(e)}")
            
    def save_settings(self):
        """حفظ الإعدادات إلى ملف"""
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.app_settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            
    def validate_path(self, path: str) -> bool:
        """التحقق من صحة مسار الحفظ"""
        try:
            if not os.path.isabs(path):
                return False
            test_file = os.path.join(path, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except Exception:
            return False
            
    def validate_inputs(self) -> Tuple[bool, str]:
        """التحقق من صحة المدخلات"""
        if not self.employee_name.value or len(self.employee_name.value.strip()) < 2:
            return False, "يجب إدخال اسم صحيح (أحرف على الأقل)"
            
        if not self.employee_id.value or not re.match(r'^\d+$', self.employee_id.value):
            return False, "يجب إدخال رقم وظيفي صحيح (أرقام فقط)"
            
        if not self.department.value or len(self.department.value.strip()) < 2:
            return False, "يجب إدخال اسم قسم صحيح"
            
        return True, ""
        
    def setup_ui_elements(self):
        """إعداد عناصر واجهة المستخدم"""
        self.setup_header()
        self.setup_sidebar()
        self.setup_input_fields()
        self.setup_qr_display()
        self.setup_action_buttons()
        self.setup_main_content()
        self.setup_footer()
        
    def setup_header(self):
        """إعداد شريط العنوان"""
        self.app_logo = ft.Icon(ft.icons.QR_CODE_SCANNER, size=40, color="white")
        self.title = ft.Text("نظام توليد QR Code المشفّر", 
                            size=26, 
                            weight=ft.FontWeight.BOLD, 
                            color="white",
                            text_align=ft.TextAlign.RIGHT)
        
        self.theme_icon = ft.IconButton(
            icon=ft.icons.DARK_MODE,
            icon_color="white",
            tooltip="تغيير السمة",
            on_click=self.change_theme
        )
        
        self.header = ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Column([self.app_logo], col={"sm": 1, "md": 1, "lg": 1}),
                    ft.Column([self.title], col={"sm": 9, "md": 10, "lg": 10}),
                    ft.Column([self.theme_icon], col={"sm": 2, "md": 1, "lg": 1}),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            bgcolor=self.colors["header_bg"],
            width=self.page.width,
        )
        
    def setup_sidebar(self):
        """إعداد الشريط الجانبي"""
        self.sidebar_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=85,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.QR_CODE,
                    selected_icon=ft.icons.QR_CODE_ROUNDED,
                    label="إنشاء QR"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SECURITY,
                    selected_icon=ft.icons.SECURITY_UPDATE_GOOD,
                    label="التشفير"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS,
                    selected_icon=ft.icons.SETTINGS_APPLICATIONS,
                    label="الإعدادات"
                ),
            ],
            bgcolor="#ffffff",
        )
        
    def setup_input_fields(self):
        """إعداد حقول إدخال البيانات"""
        field_style = {
            "border_color": self.colors["primary"],
            "focused_border_color": self.colors["secondary"],
            "width": 400,
            "text_size": 16,
            "border_radius": 8,
            "text_align": ft.TextAlign.RIGHT,
        }
        
        self.employee_name = ft.TextField(
            label="اسم الموظف",
            hint_text="أدخل الاسم الكامل",
            prefix_icon=ft.icons.PERSON,
            **field_style
        )
        
        self.employee_id = ft.TextField(
            label="الرقم الوظيفي",
            hint_text="أدخل الرقم الوظيفي",
            prefix_icon=ft.icons.BADGE,
            **field_style
        )
        
        self.department = ft.TextField(
            label="القسم",
            hint_text="أدخل اسم القسم",
            prefix_icon=ft.icons.BUSINESS,
            **field_style
        )
        
        self.additional_info = ft.TextField(
            label="معلومات إضافية (اختياري)",
            hint_text="أي معلومات إضافية عن الموظف",
            prefix_icon=ft.icons.INFO,
            multiline=True,
            min_lines=2,
            max_lines=4,
            **field_style
        )
        
    def setup_qr_display(self):
        """إعداد عناصر عرض QR Code"""
        self.employee_name_display = ft.Text("", size=14, color=self.colors["text"], text_align=ft.TextAlign.RIGHT)
        self.employee_id_display = ft.Text("", size=14, color=self.colors["text"], text_align=ft.TextAlign.RIGHT)
        self.department_display = ft.Text("", size=14, color=self.colors["text"], text_align=ft.TextAlign.RIGHT)
        
        self.progress_ring = ft.ProgressRing(
            width=40, 
            height=40, 
            stroke_width=4, 
            color=self.colors["primary"],
            visible=False
        )
        
        self.loading_text = ft.Text(
            "جارِ التوليد...",
            color=self.colors["primary"],
            size=16,
            visible=False,
            text_align=ft.TextAlign.RIGHT,
        )
        
        self.qr_image = ft.Image(
            src_base64="",
            width=300,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
        )
        
        self.qr_container = ft.Container(
            content=self.qr_image,
            alignment=ft.alignment.center,
            bgcolor="white",
            border_radius=10,
            padding=10,
            height=0,
            opacity=0,
            animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.2, "black"),
                offset=ft.Offset(0, 2),
            )
        )
        
    def setup_action_buttons(self):
        """إعداد أزرار الإجراءات"""
        self.generate_button = ft.ElevatedButton(
            "توليد QR Code",
            icon=ft.icons.QR_CODE_2,
            on_click=self.generate_qr_code,
            style=self.create_button_style(self.colors["primary"], "white"),
            width=180,
            height=45,
        )
        
        self.clear_button = ft.OutlinedButton(
            "مسح البيانات",
            icon=ft.icons.CLEANING_SERVICES,
            on_click=self.clear_fields,
            style=self.create_button_style(self.colors["text"], None),
            width=180,
            height=45,
        )
        
        self.save_button = ft.FilledTonalButton(
            "حفظ QR Code",
            icon=ft.icons.SAVE_ALT,
            on_click=self.save_qr_code,
            style=self.create_button_style(self.colors["success"], "white"),
            width=180,
            height=45,
            visible=False
        )
        
        self.result_text = ft.Text("", size=16, text_align=ft.TextAlign.RIGHT)
        self.save_result = ft.Text("", size=14, color=self.colors["text"], text_align=ft.TextAlign.RIGHT)
        
    def create_button_style(self, bgcolor: Optional[str], color: Optional[str]) -> ft.ButtonStyle:
        """إنشاء نمط موحد للأزرار"""
        return ft.ButtonStyle(
            color=color,
            bgcolor=bgcolor,
            elevation=3 if bgcolor else 0,
            animation_duration=300,
            shape=ft.RoundedRectangleBorder(radius=10),
        )
        
    def setup_main_content(self):
        """إعداد المحتوى الرئيسي للصفحة"""
        self.setup_employee_card()
        self.setup_qr_card()
        
        self.main_content = ft.Column(
            [
                self.employee_card,
                self.qr_card,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.page_layout = ft.Row(
            [
                self.sidebar_rail,
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=self.main_content,
                    expand=True,
                    padding=20,
                ),
            ],
            expand=True,
        )
        
    def setup_employee_card(self):
        """إعداد بطاقة إدخال بيانات الموظف"""
        self.employee_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.PERSON_ADD, color=self.colors["primary"], size=30),
                            title=ft.Text("بيانات الموظف", weight=ft.FontWeight.BOLD, size=18, text_align=ft.TextAlign.RIGHT),
                            subtitle=ft.Text("أدخل بيانات الموظف لتوليد QR Code مشفر", text_align=ft.TextAlign.RIGHT),
                        ),
                        ft.Divider(height=0, thickness=1),
                        ft.Container(
                            content=ft.Column(
                                [
                                    self.employee_name,
                                    ft.Container(height=10),
                                    self.employee_id,
                                    ft.Container(height=10),
                                    self.department,
                                    ft.Container(height=10),
                                    self.additional_info,
                                    ft.Container(height=20),
                                    ft.Row(
                                        [self.generate_button, self.clear_button],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=20
                                    ),
                                    ft.Container(height=15),
                                    ft.Row(
                                        [self.progress_ring, self.loading_text],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=10
                                    ),
                                    ft.Container(height=10),
                                    self.result_text,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.all(20),
                        ),
                    ]
                ),
                padding=ft.padding.all(0),
            ),
            elevation=4,
            margin=10
        )
        
    def setup_qr_card(self):
        """إعداد بطاقة عرض QR Code"""
        self.qr_card_row = ft.Row(
            [
                ft.Column(
                    [
                        self.qr_container,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("بيانات الموظف:", weight=ft.FontWeight.BOLD, size=16, text_align=ft.TextAlign.RIGHT),
                                    ft.Container(height=10),
                                    self.employee_name_display,
                                    self.employee_id_display,
                                    self.department_display,
                                    ft.Container(height=20),
                                    self.save_button,
                                    ft.Container(height=5),
                                    self.save_result,
                                ],
                            ),
                            padding=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.qr_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.QR_CODE_SCANNER, color=self.colors["primary"], size=30),
                            title=ft.Text("معاينة QR Code", weight=ft.FontWeight.BOLD, size=18, text_align=ft.TextAlign.RIGHT),
                            subtitle=ft.Text("QR Code مشفر بخوارزمية AES", text_align=ft.TextAlign.RIGHT),
                        ),
                        ft.Divider(height=0, thickness=1),
                        ft.Container(
                            content=self.qr_card_row,
                            padding=ft.padding.all(20),
                        ),
                    ]
                ),
                padding=ft.padding.all(0),
            ),
            elevation=4,
            margin=10,
            visible=False
        )
        
    def setup_footer(self):
        """إعداد تذييل الصفحة"""
        self.footer = ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Column(
                        [ft.Text("© 2025 نظام QR Code المشفر", color="#94a3b8", size=12)], 
                        col={"sm": 6, "md": 6, "lg": 6},
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Column(
                        [ft.Text("تم تطويره بواسطة Ahmad Nassif", color="#94a3b8", size=12)],
                        col={"sm": 6, "md": 6, "lg": 6},
                        horizontal_alignment=ft.CrossAxisAlignment.END
                    ),
                ],
            ),
            padding=10,
            bgcolor="#f8fafc",
            width=self.page.width,
        )
        
    def setup_event_handlers(self):
        """إعداد معالجات الأحداث"""
        self.page.on_resize = self.handle_resize
        self.sidebar_rail.on_change = self.handle_tab_selection
        
    def encrypt_data(self, data: str) -> str:
        """تشفير البيانات باستخدام AES-256-CBC"""
        cipher = AES.new(self.KEY, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return f"{iv}:{ct}"
        
    def generate_qr_code(self, e):
        """توليد QR Code من البيانات المدخلة"""
        # التحقق من صحة الإدخالات
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            self.show_error_message(error_msg)
            return

        # عرض مؤشر التحميل
        self.show_loading(True)
        
        try:
            # تجميع البيانات
            data = self.collect_employee_data()
            
            # تشفير البيانات
            encrypted_data = self.encrypt_data(data)
            
            # إنشاء QR Code
            qr_size = self.get_qr_size()
            img_str = self.create_qr_code_image(encrypted_data, qr_size)
            
            # تحديث واجهة المستخدم
            self.update_ui_after_qr_generation(img_str, qr_size, data)
            
            # الحفظ التلقائي إذا كان مفعلاً
            if self.app_settings["auto_save"]:
                self.save_qr_code(e)
            
            self.show_success_message("تم توليد QR Code بنجاح")
            
        except Exception as ex:
            self.show_error_message(f"حدث خطأ أثناء توليد QR Code: {str(ex)}")
            
        finally:
            self.show_loading(False)
    
    def collect_employee_data(self) -> str:
        """جمع بيانات الموظف من الحقول"""
        data = f"الاسم: {self.employee_name.value}\nالرقم الوظيفي: {self.employee_id.value}\nالقسم: {self.department.value}"
        if self.additional_info.value:
            data += f"\nمعلومات إضافية: {self.additional_info.value}"
        return data
        
    def get_qr_size(self) -> int:
        """الحصول على حجم QR Code بناءً على الإعدادات"""
        size_mapping = {
            "صغير": 200,
            "متوسط": 300,
            "كبير": 400,
            "كبير جداً": 500
        }
        return size_mapping.get(self.app_settings["qr_size"], 300)
        
    def create_qr_code_image(self, data: str, size: int) -> str:
        """إنشاء صورة QR Code وإرجاعها كسلسلة base64"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # إنشاء الصورة مع الألوان المخصصة
        img = qr.make_image(
            fill_color=self.app_settings.get("qr_color", "#000000"),
            back_color=self.app_settings.get("qr_bg_color", "#FFFFFF")
        )
        
        # تحويل الصورة إلى Base64
        buffered = BytesIO()
        img.save(buffered, format="PNG", quality=self.get_image_quality())
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
        
    def get_image_quality(self) -> int:
        """الحصول على جودة الصورة بناءً على الإعدادات"""
        quality_mapping = {
            "عالية جداً": 100,
            "عالية": 90,
            "متوسطة": 75,
            "منخفضة": 50
        }
        return quality_mapping.get(self.app_settings["image_quality"], 90)
        
    def update_ui_after_qr_generation(self, img_str: str, size: int, data: str):
        """تحديث واجهة المستخدم بعد توليد QR Code"""
        self.qr_image.src_base64 = img_str
        self.qr_image.width = size
        self.qr_image.height = size
        self.qr_container.height = size + 20
        self.qr_container.opacity = 1
        self.qr_image.visible = True
        
        # تحديث البيانات المعروضة
        self.employee_name_display.value = f"الاسم: {self.employee_name.value}"
        self.employee_id_display.value = f"الرقم الوظيفي: {self.employee_id.value}"
        self.department_display.value = f"القسم: {self.department.value}"
        
        # إظهار أزرار وخيارات QR Code
        self.save_button.visible = True
        self.result_text.value = "تم توليد QR Code بنجاح!"
        self.result_text.color = self.colors["success"]
        self.qr_card.visible = True
        
    def save_qr_code(self, e):
        """حفظ QR Code إلى الملف"""
        save_path = self.app_settings["save_path"]
        
        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path)
            except Exception as ex:
                self.save_result.value = f"خطأ في إنشاء المجلد: {str(ex)}"
                self.save_result.color = self.colors["error"]
                self.page.update()
                return
        
        file_path = os.path.join(save_path, f"qr_code_{self.employee_id.value}.png")
        
        try:
            img_data = base64.b64decode(self.qr_image.src_base64)
            with open(file_path, 'wb') as f:
                f.write(img_data)
            
            self.save_result.value = f"تم حفظ الصورة في: {file_path}"
            self.save_result.color = self.colors["success"]
            self.show_success_message("تم حفظ QR Code بنجاح")
            
        except Exception as ex:
            self.save_result.value = f"خطأ في حفظ الصورة: {str(ex)}"
            self.save_result.color = self.colors["error"]
            self.show_error_message(f"حدث خطأ أثناء الحفظ: {str(ex)}")
            
        self.page.update()
    
    def clear_fields(self, e):
        """مسح جميع الحقول وإعادة التعيين"""
        self.employee_name.value = ""
        self.employee_id.value = ""
        self.department.value = ""
        self.additional_info.value = ""
        self.qr_image.visible = False
        self.qr_container.height = 0
        self.qr_container.opacity = 0
        self.save_button.visible = False
        self.result_text.value = ""
        self.save_result.value = ""
        self.qr_card.visible = False
        self.employee_name_display.value = ""
        self.employee_id_display.value = ""
        self.department_display.value = ""
        self.page.update()
    
    def change_theme(self, e):
        """تغيير سمة التطبيق بين الفاتح والداكن"""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_icon.name = ft.icons.LIGHT_MODE
            self.page.bgcolor = self.colors["dark_bg"]
            self.header.bgcolor = self.colors["dark_header"]
            self.footer.bgcolor = self.colors["dark_bg"]
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_icon.name = ft.icons.DARK_MODE
            self.page.bgcolor = "#f0f4f8"
            self.header.bgcolor = self.colors["header_bg"]
            self.footer.bgcolor = "#f8fafc"
        self.page.update()
        
    def show_loading(self, show: bool):
        """عرض/إخفاء مؤشر التحميل"""
        self.loading_text.visible = show
        self.progress_ring.visible = show
        self.page.update()
        
    def show_success_message(self, message: str):
        """عرض رسالة نجاح"""
        self.result_text.value = message
        self.result_text.color = self.colors["success"]
        self.show_snackbar(message, self.colors["success"])
        
    def show_error_message(self, message: str):
        """عرض رسالة خطأ"""
        self.result_text.value = message
        self.result_text.color = self.colors["error"]
        self.show_snackbar(message, self.colors["error"])
        
    def show_snackbar(self, message: str, color: str):
        """عرض رسالة Snackbar"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color,
            action="حسناً"
        )
        self.page.snack_bar.open = True
        self.page.update()
        
    def check_responsive_layout(self, e=None):
        """التحقق من استجابة التخطيط للتغير في حجم النافذة"""
        if self.page.width is not None:
            if self.page.width < 900:
                self.is_desktop = False
                self.update_field_width(self.page.width * 0.8)
                self.sidebar_rail.visible = False
                self.page_layout.horizontal = False
                self.page_layout.controls = [
                    ft.Container(
                        content=self.main_content,
                        expand=True,
                        padding=10,
                    ),
                ]
            else:
                self.is_desktop = True
                self.update_field_width(400)
                self.sidebar_rail.visible = True
                self.page_layout.horizontal = True
                self.page_layout.controls = [
                    self.sidebar_rail,
                    ft.VerticalDivider(width=1),
                    ft.Container(
                        content=self.main_content,
                        expand=True,
                        padding=20,
                    ),
                ]
        
        self.update_card_layouts()
        self.page.update()
        
    def update_field_width(self, width: float):
        """تحديث عرض حقول الإدخال"""
        self.employee_name.width = width
        self.employee_id.width = width
        self.department.width = width
        self.additional_info.width = width
        
    def update_card_layouts(self):
        """تحديث تخطيط البطاقات حسب حجم الشاشة"""
        if not self.is_desktop:
            self.qr_card_row.horizontal = False
            self.qr_card_row.alignment = ft.MainAxisAlignment.CENTER
        else:
            self.qr_card_row.horizontal = True
            self.qr_card_row.alignment = ft.MainAxisAlignment.CENTER
            
    def handle_resize(self, e):
        """معالجة حدث تغيير حجم النافذة"""
        self.check_responsive_layout()
        
    def handle_tab_selection(self, e):
        """معالجة تغيير تبويب الشريط الجانبي"""
        selected_index = self.sidebar_rail.selected_index
        
        self.employee_card.visible = False
        self.qr_card.visible = False
        
        if selected_index == 0:
            self.employee_card.visible = True
            if self.qr_image.src_base64:
                self.qr_card.visible = True
            self.main_content.controls = [self.employee_card, self.qr_card]
            
        elif selected_index == 1:
            encryption_info_card = self.create_encryption_info_card()
            self.main_content.controls = [encryption_info_card]
            
        elif selected_index == 2:
            settings_card = self.create_settings_card()
            self.main_content.controls = [settings_card]
            
        self.page.update()
        
    def create_encryption_info_card(self):
        """إنشاء بطاقة معلومات التشفير"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.SECURITY, color=self.colors["primary"], size=30),
                            title=ft.Text("معلومات عن تشفير البيانات", weight=ft.FontWeight.BOLD, size=20, text_align=ft.TextAlign.RIGHT),
                        ),
                        ft.Divider(height=0, thickness=1),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "نظام التشفير المستخدم في التطبيق",
                                        size=18,
                                        weight=ft.FontWeight.W_500,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                    ft.Container(height=15),
                                    ft.Text(
                                        "يستخدم هذا النظام خوارزمية AES-256 (Advanced Encryption Standard) وهي معيار عالمي للتشفير المتماثل. "
                                        "تم اختيار هذه الخوارزمية لكونها:",
                                        size=14,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                    ft.Container(height=10),
                                    self.create_info_row("آمنة للغاية وتستخدم في التطبيقات الحكومية والعسكرية"),
                                    self.create_info_row("تدعم مفاتيح تشفير 256 بت (أعلى مستوى أمان)"),
                                    self.create_info_row("سريعة في التنفيذ وفعالة من حيث استهلاك الموارد"),
                                    ft.Container(height=20),
                                    ft.Text(
                                        "كيفية عمل تشفير البيانات في النظام:",
                                        size=16,
                                        weight=ft.FontWeight.W_500,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                    ft.Container(height=10),
                                    self.create_info_list([
                                        "يتم تجميع بيانات الموظف (الاسم، الرقم الوظيفي، القسم وأي معلومات إضافية)",
                                        "تُشفر البيانات باستخدام خوارزمية AES-256 في وضع CBC (Cipher Block Chaining)",
                                        "يتم إنشاء متجه التهيئة (IV) بشكل عشوائي لكل عملية تشفير",
                                        "يتم تحويل البيانات المشفرة إلى ترميز Base64",
                                        "تُدمج البيانات المشفرة مع متجه التهيئة وتُخزن في QR Code"
                                    ]),
                                    ft.Container(height=20),
                                    ft.Text(
                                        "ملاحظات مهمة حول الأمان:",
                                        size=16,
                                        weight=ft.FontWeight.W_500,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                    ft.Container(height=10),
                                    ft.Text(
                                        "يتم تخزين مفتاح التشفير في ملف محمي على الجهاز. "
                                        "لأغراض أمنية، لا يتم مشاركة هذا المفتاح مع أي جهة خارجية. "
                                        "في بيئة الإنتاج، ينصح باستخدام أنظمة إدارة المفاتيح المتخصصة.",
                                        size=14,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                ],
                            ),
                            padding=ft.padding.all(20),
                        ),
                    ]
                ),
                padding=ft.padding.all(0),
            ),
            elevation=4,
            margin=10,
        )
        
    def create_info_row(self, text: str) -> ft.Row:
        """إنشاء صف معلومات مع أيقونة"""
        return ft.Row(
            [
                ft.Icon(ft.icons.SHIELD, color=self.colors["primary"], size=20),
                ft.Text(text, size=14, text_align=ft.TextAlign.RIGHT),
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        
    def create_info_list(self, items: list) -> ft.Column:
        """إنشاء قائمة معلومات مرقمة"""
        return ft.Column(
            [ft.Text(f"{i+1}. {item}", size=14, text_align=ft.TextAlign.RIGHT) 
             for i, item in enumerate(items)],
            spacing=5,
        )
        
    def create_settings_card(self):
        """إنشاء بطاقة الإعدادات"""
        self.auto_save_switch = ft.Switch(
            value=self.app_settings["auto_save"], 
            label="حفظ تلقائي للصور"
        )
        
        self.save_path_field = ft.TextField(
            label="مسار الحفظ",
            value=self.app_settings["save_path"],
            hint_text="أدخل المسار المطلوب لحفظ الصور",
            border_color=self.colors["primary"],
            focused_border_color=self.colors["secondary"],
            prefix_icon=ft.icons.FOLDER,
            width=400,
            text_size=16,
            border_radius=8,
            text_align=ft.TextAlign.RIGHT,
        )
        
        self.image_quality_dropdown = ft.Dropdown(
            label="جودة الصورة",
            hint_text="اختر جودة صورة QR Code",
            options=[
                ft.dropdown.Option("عالية جداً"),
                ft.dropdown.Option("عالية"),
                ft.dropdown.Option("متوسطة"),
                ft.dropdown.Option("منخفضة"),
            ],
            value=self.app_settings["image_quality"],
            width=400,
            prefix_icon=ft.icons.HIGH_QUALITY,
            text_size=14,
        )
        
        self.qr_size_dropdown = ft.Dropdown(
            label="حجم QR Code",
            hint_text="اختر حجم QR Code",
            options=[
                ft.dropdown.Option("صغير"),
                ft.dropdown.Option("متوسط"),
                ft.dropdown.Option("كبير"),
                ft.dropdown.Option("كبير جداً"),
            ],
            value=self.app_settings["qr_size"],
            width=400,
            prefix_icon=ft.icons.PHOTO_SIZE_SELECT_LARGE,
            text_size=14,
        )
        
        self.qr_color_picker = ft.TextField(
            label="لون QR Code",
            value=self.app_settings.get("qr_color", "#000000"),
            hint_text="أدخل لون HEX (مثال: #000000)",
            border_color=self.colors["primary"],
            focused_border_color=self.colors["secondary"],
            prefix_icon=ft.icons.COLOR_LENS,
            width=400,
            text_size=16,
            border_radius=8,
            text_align=ft.TextAlign.RIGHT,
        )
        
        self.qr_bg_color_picker = ft.TextField(
            label="لون خلفية QR Code",
            value=self.app_settings.get("qr_bg_color", "#FFFFFF"),
            hint_text="أدخل لون HEX (مثال: #FFFFFF)",
            border_color=self.colors["primary"],
            focused_border_color=self.colors["secondary"],
            prefix_icon=ft.icons.COLOR_LENS,
            width=400,
            text_size=16,
            border_radius=8,
            text_align=ft.TextAlign.RIGHT,
        )
        
        self.language_dropdown = ft.Dropdown(
            label="اللغة",
            hint_text="اختر لغة التطبيق",
            options=[
                ft.dropdown.Option("ar", text="العربية"),
                ft.dropdown.Option("en", text="الإنجليزية"),
            ],
            value=self.app_settings.get("language", "ar"),
            width=400,
            prefix_icon=ft.icons.LANGUAGE,
            text_size=14,
        )
        
        save_settings_button = ft.ElevatedButton(
            "حفظ الإعدادات",
            icon=ft.icons.SAVE,
            on_click=self.save_settings_changes,
            style=self.create_button_style(self.colors["primary"], "white"),
            width=180,
            height=45,
        )
        
        reset_settings_button = ft.OutlinedButton(
            "استعادة الافتراضي",
            icon=ft.icons.RESTORE,
            on_click=self.reset_settings,
            style=self.create_button_style(self.colors["text"], None),
            width=180,
            height=45,
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.SETTINGS, color=self.colors["primary"], size=30),
                            title=ft.Text("إعدادات النظام", weight=ft.FontWeight.BOLD, size=20, text_align=ft.TextAlign.RIGHT),
                        ),
                        ft.Divider(height=0, thickness=1),
                        ft.Container(
                            content=ft.Column(
                                [
                                    self.create_settings_section(
                                        "إعدادات التخزين",
                                        [
                                            self.save_path_field,
                                            ft.Row(
                                                [self.auto_save_switch, ft.Text("حفظ تلقائي للصور", text_align=ft.TextAlign.RIGHT)],
                                                alignment=ft.MainAxisAlignment.END,
                                            ),
                                        ]
                                    ),
                                    
                                    self.create_settings_section(
                                        "إعدادات QR Code",
                                        [
                                            self.image_quality_dropdown,
                                            self.qr_size_dropdown,
                                            self.qr_color_picker,
                                            self.qr_bg_color_picker,
                                        ]
                                    ),
                                    
                                    self.create_settings_section(
                                        "إعدادات التطبيق",
                                        [
                                            self.language_dropdown,
                                        ]
                                    ),
                                    
                                    ft.Container(height=20),
                                    ft.Row(
                                        [save_settings_button, reset_settings_button],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=20
                                    ),
                                ],
                            ),
                            padding=ft.padding.all(20),
                        ),
                    ]
                ),
                padding=ft.padding.all(0),
            ),
            elevation=4,
            margin=10,
        )
        
    def create_settings_section(self, title: str, controls: list) -> ft.Column:
        """إنشاء قسم في إعدادات التطبيق"""
        return ft.Column(
            [
                ft.Text(
                    title,
                    size=18,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.RIGHT,
                ),
                ft.Container(height=15),
                *controls,
                ft.Container(height=20),
            ]
        )
        
    def save_settings_changes(self, e):
        """حفظ تغييرات الإعدادات"""
        # التحقق من صحة مسار الحفظ
        if not self.validate_path(self.save_path_field.value):
            self.show_error_message("مسار الحفظ غير صحيح أو غير قابل للكتابة")
            return
            
        # التحقق من صحة ألوان QR Code
        if not self.validate_color(self.qr_color_picker.value):
            self.show_error_message("لون QR Code غير صحيح. استخدم تنسيق HEX مثل #000000")
            return
            
        if not self.validate_color(self.qr_bg_color_picker.value):
            self.show_error_message("لون خلفية QR Code غير صحيح. استخدم تنسيق HEX مثل #FFFFFF")
            return
            
        # تحديث الإعدادات
        self.app_settings.update({
            "save_path": self.save_path_field.value,
            "auto_save": self.auto_save_switch.value,
            "image_quality": self.image_quality_dropdown.value,
            "qr_size": self.qr_size_dropdown.value,
            "qr_color": self.qr_color_picker.value,
            "qr_bg_color": self.qr_bg_color_picker.value,
            "language": self.language_dropdown.value
        })
        
        # حفظ الإعدادات
        self.save_settings()
        
        self.show_success_message("تم حفظ الإعدادات بنجاح")
        
    def reset_settings(self, e):
        """استعادة الإعدادات الافتراضية"""
        default_settings = {
            "save_path": os.path.join(os.path.expanduser("~"), "QR-pass"),
            "auto_save": False,
            "image_quality": "عالية",
            "qr_size": "متوسط",
            "qr_color": "#000000",
            "qr_bg_color": "#FFFFFF",
            "language": "ar"
        }
        
        # تحديث واجهة المستخدم
        self.save_path_field.value = default_settings["save_path"]
        self.auto_save_switch.value = default_settings["auto_save"]
        self.image_quality_dropdown.value = default_settings["image_quality"]
        self.qr_size_dropdown.value = default_settings["qr_size"]
        self.qr_color_picker.value = default_settings["qr_color"]
        self.qr_bg_color_picker.value = default_settings["qr_bg_color"]
        self.language_dropdown.value = default_settings["language"]
        
        # تحديث الإعدادات الحالية
        self.app_settings.update(default_settings)
        
        # حفظ الإعدادات
        self.save_settings()
        
        self.show_success_message("تم استعادة الإعدادات الافتراضية")
        
    def validate_color(self, color: str) -> bool:
        """التحقق من صحة تنسيق لون HEX"""
        return re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color) is not None
        
    def run(self):
        """تشغيل التطبيق"""
        self.page.add(
            ft.Column(
                [
                    self.header,
                    self.page_layout,
                    self.footer,
                ],
                spacing=0,
                expand=True,
            )
        )
        
        # التحقق من التخطيط الأولي
        self.check_responsive_layout()

def main(page: ft.Page):
    app = QRCodeGeneratorApp(page)
    app.run()

ft.app(target=main)
