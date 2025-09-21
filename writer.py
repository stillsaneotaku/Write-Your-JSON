import tkinter as tk
import json as js
from tkinter import ttk, messagebox, filedialog
import re
import sys
import os

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Write Your JSON")
        
        if getattr(sys, 'frozen', False):
            # Running as a bundled exe
            base_path = sys._MEIPASS
        else:
            # Running as a script
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "icon.ico")
        self.root.iconbitmap(icon_path)

        # Vars
        self.node_board = []
        self.pasted = False

        # Set window size and position
        wwidth, wheight = self.get_screen_size()
        wwidth = int(wwidth * 0.5)
        wheight = int(wheight * 0.5)

        # Frame Constructors
        self.root.frameT = tk.Frame(self.root, bg="gray", height = wheight/16, width = wwidth)
        self.root.frameT.pack(side="top")
        self.root.frameL = tk.Frame(self.root, bg="purple", height = wheight, width = wwidth/2)
        self.root.frameL.pack(side="left")
        self.root.frameUL = tk.Frame(self.root.frameL, bg="green", height = wheight/2, width = wwidth/2)
        self.root.frameUL.pack(side="top", fill="both", expand=True)
        self.root.frameBL = tk.Frame(self.root.frameL, bg="blue", height = wheight/2, width = wwidth/2)
        self.root.frameBL.pack(side="bottom", fill="both", expand=True)
        self.root.frameR = tk.Frame(self.root, bg="black", height = wheight, width = wwidth/2)
        self.root.frameR.pack(side="right")

        # Hierarchy Panel
        self.hierarchy = ttk.Treeview(self.root.frameUL)
        self.hierarchy.pack(side="left", fill="both", expand=True)
        # -- Binding
        self.selected = self.hierarchy.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Top Frame Widgets
        self.root.credits = tk.Label(self.root.frameT, text="Project created by John B. [https://github.com/stillsaneotaku]", anchor="w")
        self.root.credits.pack(side="left", fill="x", expand=True)

        # Upper Left Frame Widgets
        self.root.openfile = tk.Button(self.root.frameUL, text="Open File", command=self.ask_open_file)
        self.root.openfile.pack(side="top", fill="both", expand="True")
        self.root.extractjson = tk.Button(self.root.frameUL, text="Export", command=self.extract_file)
        self.root.extractjson.pack(side="top", fill="both", expand="True")
        self.root.deletenode = tk.Button(self.root.frameUL, text="Delete Node", command=lambda: self.delete_node(self.hierarchy.selection()))
        self.root.deletenode.pack(side="top", fill="both", expand="True")
        self.root.addnode = tk.Button(self.root.frameUL, text="Add Node", command=lambda: self.add_node(self.hierarchy.selection()))
        self.root.addnode.pack(side="top", fill="both", expand="True")
        self.root.addrootnode = tk.Button(self.root.frameUL, text="Add Root Node", command=lambda: self.add_root_node())
        self.root.addrootnode.pack(side="top", fill="both", expand="True")
        self.root.copynode = tk.Button(self.root.frameUL, text="Copy Node", command=lambda: self.copy_node(self.hierarchy.selection()))
        self.root.copynode.pack(side="top", fill="both", expand="True")
        self.root.pastenode = tk.Button(self.root.frameUL, text="Paste", command=lambda: self.paste_node(self.hierarchy.selection()))
        self.root.pastenode.pack(side="top", fill="both", expand="True")
        self.root.pasterootnode = tk.Button(self.root.frameUL, text="Paste as Root", command=lambda: self.paste_root_node())
        self.root.pasterootnode.pack(side="top", fill="both", expand="True")
        # Binding for rename
        self.hierarchy.bind("<Double-1>", self.change_node_label)

        # Bottom Left Frame Widgets
        self.root.instructions = tk.Label(self.root.frameBL, text="Enter node data below.")
        self.root.instructions.pack(side="top", fill="both", expand=True)
        self.root.textbox = tk.Text(self.root.frameBL, height=wheight//16, width=wwidth//16)
        self.root.textbox.pack()
        # Binding for text box changes
        self.root.textbox.bind("<FocusIn>", self.write_to_node)

        # Right Frame Widgets
        self.root.jsonview = tk.Text(self.root.frameR, bg="black", fg="white", wrap="none")
        self.json_yscrollbar = tk.Scrollbar(self.root.frameR, orient="vertical", command=self.root.jsonview.yview)
        self.json_xscrollbar = tk.Scrollbar(self.root.frameR, orient="horizontal", command=self.root.jsonview.xview)
        self.root.jsonview.configure(yscrollcommand=self.json_yscrollbar.set, xscrollcommand=self.json_xscrollbar.set)
        self.json_yscrollbar.pack(side="right", fill="y")
        self.json_xscrollbar.pack(side="bottom", fill="x")
        self.root.jsonview.pack(side="left", fill="both", expand=True)
 
        # Example hierarchy structure
        root_node = self.hierarchy.insert("", "end", text="Root")
        child1 = self.hierarchy.insert(root_node, "end", text="Child 1", values="Roberto,25")
        child2 = self.hierarchy.insert(root_node, "end", text="Child 2")
        self.hierarchy.insert(child1, "end", text="Grandchild 1")
        self.hierarchy.insert(child2, "end", text="Grandchild 2")
        self.update_jsonview()

        self.root.geometry(f"{wwidth}x{wheight}+{wwidth//2}+{wheight//2}")
        self.root.resizable(False, False)

    def get_screen_size(self):
        return self.root.winfo_screenwidth(), self.root.winfo_screenheight()
    
    def ask_open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Open File"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = js.load(f)
                    self.hierarchy.delete(*self.hierarchy.get_children())
                    self.json_to_hierarchy(data)
                    self.update_jsonview()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def extract_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save File"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.convert_to_json())

    def add_root_node(self):
        count = self.hierarchy.get_children("")
        count = len(count)

        self.hierarchy.insert("", "end", text=f"New Root {count+1}")
        self.update_jsonview()
        
    def add_node(self, items):
        count = self.hierarchy.get_children(items[0])
        count = len(count)
        for item in items:
            if item:
                level = self.get_tree_level(item)
                self.hierarchy.insert(item, "end", text=f"[{level}]Child{count+1}")
                self.children_exists(item)
        self.update_jsonview()

    def delete_node(self, items):
        for item in items:
            if item:
                parent = self.hierarchy.parent(item)
                if (parent == "" and self.get_siblings(item) == 1):
                    messagebox.showerror("Human Error!", "You cannot delete the only root node")
                    return
                self.hierarchy.delete(item)
        self.update_jsonview()

    def on_tree_select(self, event): # handles event when users select a node
        selected = self.hierarchy.selection()
        if selected:
            node_id = selected[0]
            node_text = self.hierarchy.item(node_id, "values")
            print("Selected node:", node_text)
            if self.children_exists(node_id):
                self.root.textbox.delete("1.0", tk.END)
                self.root.textbox.config(state="disabled")
                #print("Node has children and cannot be edited.", self.root.textbox.cget("state"))
            else:
                self.root.textbox.config(state="normal")
                self.root.textbox.delete("1.0", tk.END)
            self.write_to_node(event=None)
        return selected
    
    def get_tree_level(self, item):
        level = 0
        while self.hierarchy.parent(item):
            item = self.hierarchy.parent(item)
            level += 1
        return level
    
    def get_siblings(self, item):
        parent = self.hierarchy.parent(item)
        siblings = self.hierarchy.get_children(parent)
        return len(siblings) 
    
    def children_exists(self, item):
        children = []
        children = self.hierarchy.get_children(item)
        if len(children) != 0:
            self.hierarchy.item(item, values="")
            return True
        return False
    
    def is_descendant(self, ancestor, node):
        parent = self.hierarchy.parent(node)
        while parent:
            if parent == ancestor:
                return True
            parent = self.hierarchy.parent(parent)
        return False
    
    # --- COPY PASTE METHODS ---
    def get_subtree_data(self, node_id):
        node_data = {
            'text': self.hierarchy.item(node_id, 'text'),
            'values': self.hierarchy.item(node_id, 'values'),
            'children': [self.get_subtree_data(child) for child in self.hierarchy.get_children(node_id)]
        }
        return node_data

    def paste_subtree_data(self, parent_id, subtree_data):
        new_id = self.hierarchy.insert(parent_id, 'end', text=subtree_data['text'], values=subtree_data['values'])
        for child_data in subtree_data['children']:
            self.paste_subtree_data(new_id, child_data)
        return new_id

    def copy_node(self, item):
        if self.node_board:
            self.node_board.clear()
        if len(item) > 1:
            messagebox.showerror("Human Error!", "You can only copy one node from a level at a time")
            return
        self.node_board = [self.get_subtree_data(item[0])]

    def copy_subtree(self, source_id, target_id):
        for child in self.hierarchy.get_children(source_id):
            child_text = self.hierarchy.item(child, "text")
            child_values = self.hierarchy.item(child, "values")
            new_child_id = self.hierarchy.insert(target_id, "end", text=child_text, values=child_values)
            self.copy_subtree(child, new_child_id)

    def paste_node(self, parents):
        if not self.node_board or not parents:
            messagebox.showerror("Human Error!", "No node copied or no target selected")
            return
        for parent_id in parents:
            for subtree in self.node_board:
                base_name = re.sub(r"\s*\d*$", "", subtree['text'])
                count = self.count_nodes_with_base_name(base_name)
                new_text = f"{base_name} {count+1}" if count > 0 else base_name
                subtree_copy = dict(subtree)  
                subtree_copy['text'] = new_text
                self.paste_subtree_data(parent_id, subtree_copy)
        self.update_jsonview()

    def paste_root_node(self):
        if not self.node_board:
            messagebox.showerror("Human Error!", "No node copied or no target selected")
            return
        for subtree in self.node_board:
            base_name = re.sub(r"\s*\d*$", "", subtree['text'])
            count = self.count_nodes_with_base_name(base_name)
            new_text = f"{base_name} {count+1}" if count > 0 else base_name
            subtree_copy = dict(subtree)  # shallow copy
            subtree_copy['text'] = new_text
            self.paste_subtree_data("", subtree_copy)
        self.update_jsonview()

    # --- DATA MANIPULATION METHODS ---
    
    def change_node_label(self, event):
        item = self.hierarchy.identify_row(event.y)
        if not item:
            return
        x, y, width, height = self.hierarchy.bbox(item)
        text = self.hierarchy.item(item, "text")
        entry = tk.Entry(self.root.frameUL)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, text)
        entry.focus_set()

        def rename_end(event=None):
            new_text = entry.get()
            self.hierarchy.item(item, text=new_text)
            entry.destroy()
        entry.bind("<Return>", rename_end)
        entry.bind("<FocusOut>", rename_end)
        self.update_jsonview()

    def write_to_node(self, event):
        if len(self.hierarchy.selection()) > 1:
            return
        self.root.textbox.delete("1.0", tk.END)
        item = self.hierarchy.selection()
        value = self.hierarchy.item(item, "values")
        if value and value[0]:
            self.root.textbox.insert("1.0", value[0])

        def save_textbox_to_node(event=None):
            new_data = self.root.textbox.get("1.0", tk.END)
            self.hierarchy.item(item, values=(new_data[0:len(new_data)-1],))

        self.root.textbox.bind("<FocusOut>", save_textbox_to_node)
        self.update_jsonview()

    # -- JSON VIEWING METHODS --

    def update_jsonview(self):
        # Save current scroll position
        yview = self.root.jsonview.yview()
        xview = self.root.jsonview.xview()
        json_str = self.convert_to_json()
        self.root.jsonview.config(state="normal")
        self.root.jsonview.delete("1.0", tk.END)
        self.root.jsonview.insert(tk.END, json_str)
        self.root.jsonview.config(state="disabled")
        # Restore scroll position
        self.root.jsonview.yview_moveto(yview[0])
        self.root.jsonview.xview_moveto(xview[0])

    # -- JSON CONVERSION METHODS --

    def convert_to_json(self):
        roots = self.hierarchy.get_children("")
        if not roots:
            return "{}"
        data = {}
        for r in roots:
            root_text = self.hierarchy.item(r, "text")
            data[root_text] = self.format_nodes(r)
        return js.dumps(data, indent=4)

    def format_nodes(self, item): # takes an item and returns its data in dict or string form, handles similarly named items
        children = self.hierarchy.get_children(item)
        value = self.hierarchy.item(item, "values")
        if children:
            node_data = {}
            name_count = {}
            for child in children:
                child_text = self.hierarchy.item(child, "text")
                key = child_text
                if key in name_count:
                    name_count[key] += 1
                    key = f"{child_text} {name_count[child_text]}"
                else:
                    name_count[key] = 1
                node_data[key] = self.format_nodes(child)
            return node_data
        else:
            return value[0] if value and value[0] else ""
        
    def json_to_hierarchy(self, data, parent=""):
        if isinstance(data, dict):
            for key, value in data.items():
                node_id = self.hierarchy.insert(parent, "end", text=key)
                self.json_to_hierarchy(value, node_id)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                node_id = self.hierarchy.insert(parent, "end", text=f"Item {index+1}")
                self.json_to_hierarchy(item, node_id)
        else:
            self.hierarchy.item(parent, values=(str(data),))

    def count_nodes_with_base_name(self, base_name):
        count = 0
        children = self.hierarchy.get_children("")
        for i in children:
            text = self.hierarchy.item(i, "text")
            match = re.match(rf"^{re.escape(base_name)}\s*\d*$", text)
            if match:
                count += 1
        return count

    def get_all_parents(self, node_id):
        parents = []
        parent = self.hierarchy.parent(node_id)
        while parent:
            name1 = re.sub(r"\s*\d*$", "", self.hierarchy.item(parent, "text"))
            parents.append(name1)
            parent = self.hierarchy.parent(parent)
        print(parents)
        return parents

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()