import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json

class Document:
    """Класс для представления документа"""
    def __init__(self, master, text_widget, filepath=None):
        self.master = master
        self.text_widget = text_widget
        self.filepath = filepath
        self.modified = False
        self.tab_index = None
        
    @property
    def has_name(self):
        """Проверяет, есть ли у документа имя файла"""
        return self.filepath is not None and self.filepath != ""
    
    @property
    def short_name(self):
        """Возвращает короткое имя файла для отображения на вкладке"""
        if self.has_name:
            return os.path.basename(self.filepath)
        return "Без имени"
    
    @property
    def full_name(self):
        """Возвращает полное имя файла"""
        return self.filepath if self.has_name else "Без имени"
    
    def open_file(self, filepath):
        """Открывает файл"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, content)
            self.filepath = filepath
            self.modified = False
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
            return False
    
    def save_file(self):
        """Сохраняет файл"""
        if not self.has_name:
            return False
        
        try:
            content = self.text_widget.get(1.0, tk.END)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.modified = False
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            return False
    
    def save_as(self, filepath):
        """Сохраняет файл с новым именем"""
        try:
            content = self.text_widget.get(1.0, tk.END)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.filepath = filepath
            self.modified = False
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            return False


class RecentList:
    """Класс для работы со списком последних файлов"""
    def __init__(self, filename='recent_files.json'):
        self.filename = filename
        self.max_items = 5
    
    def load_data(self):
        """Загружает список последних файлов"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self, files):
        """Сохраняет список последних файлов"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(files, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add(self, filepath):
        """Добавляет файл в список недавних"""
        files = self.load_data()
        
        # Удаляем файл, если он уже есть в списке
        if filepath in files:
            files.remove(filepath)
        
        # Добавляем файл в начало списка
        files.insert(0, filepath)
        
        # Ограничиваем размер списка
        files = files[:self.max_items]
        
        # Сохраняем обновленный список
        self.save_data(files)


class TextEditor:
    """Основной класс текстового редактора"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Текстовый редактор")
        self.root.geometry("1000x600")
        
        # Инициализация компонентов
        self.recent_list = RecentList()
        self.documents = []  # Список открытых документов
        self.current_doc = None
        
        # Создание интерфейса
        self.create_menu()
        self.create_widgets()
        
        # Загрузка списка последних файлов
        self.load_recent_files()
        
        # Создание первого документа
        self.new_doc()
        
        # Привязка горячих клавиш
        self.bind_hotkeys()
        
    def create_menu(self):
        """Создает главное меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        file_menu.add_command(label="Новый", command=self.new_doc, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_doc, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_doc, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_doc_as)
        file_menu.add_command(label="Закрыть", command=self.close_doc, accelerator="Ctrl+W")
        file_menu.add_separator()
        
        # Подменю "Недавние"
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Недавние", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_app, accelerator="Alt+F4")
        
        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        
        # Меню "Вид"
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        view_menu.add_command(label="Увеличить шрифт", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Уменьшить шрифт", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Сбросить масштаб", command=self.zoom_reset, accelerator="Ctrl+0")
        
    def create_widgets(self):
        """Создает виджеты интерфейса"""
        # Создаем панель вкладок
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем обработчик событий для вкладок
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Создаем статус бар
        self.status_bar = tk.Label(self.root, text="Готово", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def new_doc(self):
        """Создает новый документ"""
        # Создаем фрейм для вкладки
        frame = tk.Frame(self.tab_control)
        
        # Создаем текстовое поле
        text_widget = tk.Text(
            frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            undo=True,
            maxundo=100
        )
        
        # Добавляем полосу прокрутки
        scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Размещаем виджеты
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Создаем документ
        doc = Document(self.root, text_widget)
        
        # Добавляем вкладку
        index = len(self.documents)
        self.tab_control.add(frame, text=doc.short_name)
        doc.tab_index = index
        
        # Добавляем документ в список
        self.documents.append(doc)
        
        # Делаем новую вкладку активной
        self.tab_control.select(index)
        
        # Привязываем обработчик изменений текста
        text_widget.bind("<<Modified>>", lambda e: self.on_text_modified(doc))
        
        # Устанавливаем фокус на текстовое поле
        text_widget.focus_set()
        
    def open_doc(self, filepath=None):
        """Открывает существующий документ"""
        if not filepath:
            filepath = filedialog.askopenfilename(
                title="Открыть файл",
                filetypes=[
                    ("Текстовые файлы", "*.txt"),
                    ("Python файлы", "*.py"),
                    ("Все файлы", "*.*")
                ]
            )
            
        if filepath:
            # Проверяем, не открыт ли уже файл
            if self.doc_opened(filepath):
                messagebox.showinfo("Информация", "Файл уже открыт")
                return
            
            # Создаем новый документ
            self.new_doc()
            doc = self.current_doc
            
            # Открываем файл
            if doc.open_file(filepath):
                # Обновляем заголовок вкладки
                self.tab_control.tab(doc.tab_index, text=doc.short_name)
                
                # Добавляем в список последних файлов
                self.recent_list.add(filepath)
                self.update_recent_menu()
            else:
                # Если не удалось открыть файл, закрываем созданную вкладку
                self.close_doc_by_index(doc.tab_index)
    
    def save_doc(self):
        """Сохраняет текущий документ"""
        if self.current_doc:
            if self.current_doc.has_name:
                if self.current_doc.save_file():
                    # Обновляем заголовок вкладки
                    self.tab_control.tab(
                        self.current_doc.tab_index, 
                        text=self.current_doc.short_name
                    )
                    self.status_bar.config(text="Файл сохранен")
                    
                    # Добавляем в список последних файлов
                    self.recent_list.add(self.current_doc.filepath)
                    self.update_recent_menu()
                else:
                    self.status_bar.config(text="Ошибка сохранения")
            else:
                # Если у документа нет имени, вызываем "Сохранить как"
                self.save_doc_as()
    
    def save_doc_as(self):
        """Сохраняет документ с новым именем"""
        if self.current_doc:
            filepath = filedialog.asksaveasfilename(
                title="Сохранить как",
                defaultextension=".txt",
                filetypes=[
                    ("Текстовые файлы", "*.txt"),
                    ("Python файлы", "*.py"),
                    ("Все файлы", "*.*")
                ]
            )
            
            if filepath:
                if self.current_doc.save_as(filepath):
                    # Обновляем заголовок вкладки
                    self.tab_control.tab(
                        self.current_doc.tab_index, 
                        text=self.current_doc.short_name
                    )
                    self.status_bar.config(text="Файл сохранен")
                    
                    # Добавляем в список последних файлов
                    self.recent_list.add(filepath)
                    self.update_recent_menu()
                else:
                    self.status_bar.config(text="Ошибка сохранения")
    
    def close_doc(self):
        """Закрывает текущий документ"""
        if self.current_doc:
            # Проверяем, нужно ли сохранить изменения
            if self.current_doc.modified:
                response = messagebox.askyesnocancel(
                    "Сохранение",
                    f"Сохранить изменения в файле '{self.current_doc.short_name}'?"
                )
                
                if response is None:  # Отмена
                    return
                elif response:  # Да
                    self.save_doc()
            
            # Закрываем вкладку
            self.close_doc_by_index(self.current_doc.tab_index)
    
    def close_doc_by_index(self, index):
        """Закрывает документ по индексу"""
        if 0 <= index < len(self.documents):
            # Удаляем вкладку
            self.tab_control.forget(index)
            
            # Удаляем документ из списка
            del self.documents[index]
            
            # Обновляем индексы оставшихся документов
            for i in range(index, len(self.documents)):
                self.documents[i].tab_index = i
            
            # Если остались открытые документы, выбираем последний
            if self.documents:
                self.tab_control.select(len(self.documents) - 1)
    
    def doc_opened(self, filename):
        """Проверяет, открыт ли уже файл"""
        for doc in self.documents:
            if doc.filepath == filename:
                return True
        return False
    
    def open_doc_by_recent_index(self, index):
        """Открывает документ из списка последних файлов по индексу"""
        files = self.recent_list.load_data()
        if 0 <= index < len(files):
            self.open_doc(files[index])
    
    def on_tab_changed(self, event):
        """Обработчик события изменения активной вкладки"""
        selected = self.tab_control.select()
        if selected:
            tab_index = self.tab_control.index(selected)
            if 0 <= tab_index < len(self.documents):
                self.current_doc = self.documents[tab_index]
                
                # Обновляем статус бар
                if self.current_doc.has_name:
                    self.status_bar.config(text=f"{self.current_doc.full_name} - {len(self.documents)} документов")
                else:
                    self.status_bar.config(text=f"Без имени - {len(self.documents)} документов")
    
    def on_text_modified(self, doc):
        """Обработчик изменения текста"""
        if doc.text_widget.edit_modified():
            doc.modified = True
            
            # Добавляем звездочку к названию вкладки
            tab_text = doc.short_name
            if doc.modified:
                tab_text = "*" + tab_text
            
            self.tab_control.tab(doc.tab_index, text=tab_text)
            doc.text_widget.edit_modified(False)
    
    def load_recent_files(self):
        """Загружает список последних файлов"""
        self.update_recent_menu()
    
    def update_recent_menu(self):
        """Обновляет меню последних файлов"""
        # Очищаем меню
        self.recent_menu.delete(0, tk.END)
        
        # Загружаем список файлов
        files = self.recent_list.load_data()
        
        if files:
            for i, filepath in enumerate(files):
                filename = os.path.basename(filepath)
                self.recent_menu.add_command(
                    label=f"{i+1}. {filename}",
                    command=lambda f=filepath: self.open_doc(f)
                )
        else:
            self.recent_menu.add_command(label="Нет недавних файлов", state=tk.DISABLED)
    
    def undo(self):
        """Отмена последнего действия"""
        if self.current_doc:
            try:
                self.current_doc.text_widget.edit_undo()
            except:
                pass
    
    def redo(self):
        """Повтор последнего действия"""
        if self.current_doc:
            try:
                self.current_doc.text_widget.edit_redo()
            except:
                pass
    
    def cut(self):
        """Вырезать выделенный текст"""
        if self.current_doc:
            self.current_doc.text_widget.event_generate("<<Cut>>")
    
    def copy(self):
        """Копировать выделенный текст"""
        if self.current_doc:
            self.current_doc.text_widget.event_generate("<<Copy>>")
    
    def paste(self):
        """Вставить текст из буфера обмена"""
        if self.current_doc:
            self.current_doc.text_widget.event_generate("<<Paste>>")
    
    def select_all(self):
        """Выделить весь текст"""
        if self.current_doc:
            self.current_doc.text_widget.tag_add(tk.SEL, "1.0", tk.END)
            self.current_doc.text_widget.mark_set(tk.INSERT, "1.0")
            self.current_doc.text_widget.see(tk.INSERT)
            return "break"
    
    def zoom_in(self):
        """Увеличить шрифт"""
        for doc in self.documents:
            current_font = doc.text_widget.cget("font")
            font_parts = current_font.split()
            if len(font_parts) >= 2:
                try:
                    size = int(font_parts[1])
                    doc.text_widget.config(font=(font_parts[0], size + 1))
                except:
                    pass
    
    def zoom_out(self):
        """Уменьшить шрифт"""
        for doc in self.documents:
            current_font = doc.text_widget.cget("font")
            font_parts = current_font.split()
            if len(font_parts) >= 2:
                try:
                    size = int(font_parts[1])
                    if size > 6:
                        doc.text_widget.config(font=(font_parts[0], size - 1))
                except:
                    pass
    
    def zoom_reset(self):
        """Сбросить масштаб шрифта"""
        for doc in self.documents:
            doc.text_widget.config(font=("Consolas", 12))
    
    def bind_hotkeys(self):
        """Привязывает горячие клавиши"""
        # Новый документ
        self.root.bind("<Control-n>", lambda e: self.new_doc())
        self.root.bind("<Control-N>", lambda e: self.new_doc())
        
        # Открыть документ
        self.root.bind("<Control-o>", lambda e: self.open_doc())
        self.root.bind("<Control-O>", lambda e: self.open_doc())
        
        # Сохранить документ
        self.root.bind("<Control-s>", lambda e: self.save_doc())
        self.root.bind("<Control-S>", lambda e: self.save_doc())
        
        # Закрыть документ
        self.root.bind("<Control-w>", lambda e: self.close_doc())
        self.root.bind("<Control-W>", lambda e: self.close_doc())
        
        # Отмена/повтор
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        
        # Вырезать/копировать/вставить
        self.root.bind("<Control-x>", lambda e: self.cut())
        self.root.bind("<Control-c>", lambda e: self.copy())
        self.root.bind("<Control-v>", lambda e: self.paste())
        
        # Выделить все
        self.root.bind("<Control-a>", lambda e: self.select_all())
        
        # Масштаб
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.zoom_reset())
        
        # Выход
        self.root.bind("<Alt-F4>", lambda e: self.exit_app())
    
    def exit_app(self):
        """Выход из приложения"""
        # Проверяем каждый документ на наличие несохраненных изменений
        for doc in self.documents:
            if doc.modified:
                response = messagebox.askyesnocancel(
                    "Сохранение",
                    f"Сохранить изменения в файле '{doc.short_name}'?"
                )
                
                if response is None:  # Отмена
                    return
                elif response:  # Да
                    # Делаем документ текущим
                    self.tab_control.select(doc.tab_index)
                    self.current_doc = doc
                    
                    if doc.has_name:
                        doc.save_file()
                    else:
                        self.save_doc()
        
        # Закрываем приложение
        self.root.destroy()
    
    def run(self):
        """Запускает главный цикл приложения"""
        self.root.mainloop()


# Запуск приложения
if __name__ == "__main__":
    app = TextEditor()
    app.run()