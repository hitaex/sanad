### Hadith Chain Application File Format (.amn) - Detailed Specification

The `.amn` (Al-Ameenah / Isnad) file format is a comprehensive JSON-based structure designed for the Hadith Chain Visualization Application. It serves as a universal sharing method, preserving not only the hierarchical data but also the exact visual layout and styling of the narration tree.
Which uses JSON syntax for simplicity and portability.
#### Key Components

1.  **Header Metadata**: Basic information about the Hadith and the file creation.
2.  **Hierarchical Chain**: A recursive N-ary tree structure of narrator nodes.
3.  **Visual Attributes**: Precise coordinates, colors, and font styles for every node and text box.
4.  **Independent Text Boxes**: Free-floating annotations preserved with their visual properties.
5.  **Embedded Biographies**: Full metadata for custom and blank narrators ensuring portability.

---

#### File Syntax (JSON)

```json
{
  "hadith_name": "Hadith Name",
  "matn": "Text of the Hadith...",
  "layout_style": 0,
  "chain": [
    {
      "type": "NARRATOR",
      "narrator_id": 123,
      "narrator_name": "Narrator Name",
      "method": "حدثنا",
      "visual": {
        "x": 500.0,
        "y": 200.0,
        "width": 220.0,
        "height": 100.0,
        "color": "#ffffff",
        "border_color": "#505050",
        "text_color": "#000000",
        "font_size": 12,
        "bold": true,
        "italic": false
      },
      "details": {
        "id": 123,
        "name": "Narrator Name",
        "basic_info": { "Death": "110 AH" },
        "jarh_tadil": [],
        "is_custom": true
      },
      "children": [
        {
          "type": "NARRATOR",
          "narrator_id": 456,
          "narrator_name": "Child Narrator",
          "method": "عن",
          "visual": { ... },
          "children": []
        }
      ]
    }
  ],
  "text_boxes": [
    {
      "x": -100.0,
      "y": -50.0,
      "width": 200.0,
      "height": 60.0,
      "text": "Annotation text",
      "color": "#ffffdc",
      "border_color": "#787878",
      "text_color": "#000000",
      "font_size": 12,
      "bold": false,
      "italic": true
    }
  ],
  "created": "2026-02-10T01:55:00"
}
```

---

#### Detailed Attribute Descriptions

| Attribute | Description |
| :--- | :--- |
| `visual.x / y` | The absolute scene coordinates of the item. |
| `visual.color` | The background (brush) color in hex format (e.g., `#ffffff`). |
| `visual.border_color` | The border (pen) color in hex format. |
| `visual.text_color` | The color of the label text. |
| `visual.font_size` | Integer value for font point size. |
| `visual.bold / italic` | Boolean flags for font weight and style. |
| `method` | The narration method (arrow attribute). The arrow color is derived from this and restored automatically based on the application's strength grading. |

#### Usage
-   **Exporting**: Click **"💾 حفظ"** in the Graph Tab or toolbar. Choose `.amn` to save the full visual state.
-   **Importing**: Click **"📂 فتح"** in the Graph Tab or toolbar. The application will reconstruct the tree, placing every node and text box in its exact saved position with all styling intact.
-   **Universal Sharing**: `.amn` files are self-contained. Custom narrators created on one machine will display correctly on another, even if they aren't in the recipient's local database.
