# Hadith Chain Visualization Application (Isnad Tool)

Welcome to the **Hadith Chain Visualization Application**, a specialized tool designed for researchers, students, and scholars of Hadith. This application allows you to browse an extensive database of narrators, build complex hierarchical narration chains (Isnad), and export them as professional-grade visualizations.

---

## 🚀 Key Features

### 1. **Extensive Narrator Database**
- **Deep Research**: Access nearly 19,000 narrator records.
- **Biographical Details**: View names, nicknames (Kunya), lineages (Nasab), death dates, and Ibn Hajar's rankings.
- **Scholar Critiques**: Read detailed Jarh wa Ta'dil (criticism and praise) comments from various scholars.

### 2. **Advanced Search & Filter**
- **Fuzzy Search**: Find narrators even with partial or approximate names.
- **Tabaqat Filtering**: Narrow down results by the 12 generations (Tabaqat) of narrators.
- **Real-time Results**: Search results update as you type or apply filters.

### 3. **Hierarchical Isnad Visualization**
- **N-ary Tree Structure**: Create direct parent-to-child connections with unlimited branching.
- **Dynamic Layouts**: Choose between **Vertical Tree**, **Horizontal Tree**, or **Pyramid** layouts.
- **Visual Strength Indicators**: Narration methods (e.g., "حدثنا", "عن") are color-coded from Green (strongest) to Red (weakest).

### 4. **Interactive Graph Building**
- **Drag & Drop**: Reposition nodes anywhere on the canvas.
- **Add Child Workflow**: Right-click a node and press **"+"** to set it as a parent; then select any narrator to add them as a descendant.
- **Blank Boxes & Annotations**: Add editable "Blank Boxes" for narrators not in the database, or free-floating text boxes for general notes.
- **Text Styling**: Fully customize text size, color, bold, and italic properties.

### 5. **Universal File Format (.amn)**
- **Self-Contained Files**: Save your work in the custom `.amn` format which embeds all visual coordinates, styles, and narrator biographies.
- **Portability**: Share your chains with others; they will see exactly what you designed, even if they don't have your local database.

---

## 📖 User Guide

### **Tab 1: 🔍 Search (البحث في الرواة)**
1. Enter the narrator's name in the search bar.
2. Select the search type (Fuzzy/Exact).
3. Use the **Tabaqa Filter** to narrow down by generation.
4. Double-click a result to view full biographical details in the left panel.

### **Tab 2: 🌳 Graphing (رسم السند)**
#### **Building the Chain:**
- **Adding Root Nodes**: Search for a narrator in the right panel and click **"➕ إضافة راوٍ"**.
- **Adding Children**: 
    1. Right-click a node on the canvas.
    2. Click **"➕ إضافة راوٍ تابع "**. The node will be highlighted with a blue dashed border.
    3. Select a narrator from the list or click **"📝 إضافة صندوق نص"** to add them under the highlighted parent.
- **Adding Branches**: You can add multiple children to the same parent to create branches.

#### **Editing & Styling:**
- **Move Items**: Left-click and drag any node or text box.
- **Edit Text**: Double-click inside a "Blank Box" or "Text Box" to edit its content.
- **Style Toolbar**: Select an item and use the toolbar (B, I, Size, Color) to change its appearance.
- **Delete Items**: Select an item and press `Delete` or `Ctrl+Delete`.

#### **Visualizing:**
- **Layouts**: Use the dropdown in the left panel to switch between Vertical, Horizontal, and Pyramid views.
- **Zoom**: Use the mouse wheel or the zoom buttons (+, -, Fit) in the toolbar.
- **Multi-Select**: Hold the **Right Mouse Button** and drag to select multiple items at once.

### **Tab 3: ⚙️ Settings (الإعدادات)**
- **Manage Custom Narrators**: View all narrators you've created during your session.
- **Permanent Save**: Click **"Save Temporary Narrators to JSON"** to store your custom narrators permanently in the `Data/JSON/custom_narrators` folder.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| **Ctrl + C** | Copy selected node(s) |
| **Ctrl + X** | Cut selected node(s) |
| **Ctrl + V** | Paste as child of selected parent |
| **Ctrl + Z** | Undo last action |
| **Ctrl + Y** | Redo last action |
| **Ctrl + A** | Select all items on canvas |
| **Delete** / **Ctrl+Del** | Delete selected item(s) |
| **Ctrl + S** | Save chain to `.amn` file |
| **Ctrl + O** | Open an existing `.amn` file |
| **Ctrl + E** | Export as PNG image |
| **Ctrl + P** | Export as PDF |

---

## 🛠️ Data Folders
- `Data/JSON/narrators`: Contains the core database files.
- `Data/JSON/custom_narrators`: Stores narrators created by the user.
- `info/`: Contains documentation and file format specifications.
