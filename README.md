# Product Search Agent

This Python script is an automated agent that reads a list of products from an Excel file and searches the internet to find those exact items on e-commerce websites (like Amazon and Flipkart). It then acts like a human reviewer: it compares the name of the product you searched for with the name of the product it found, calculates a **similarity score**, and determines if the result needs a human to double-check it.

---

## � Getting Started (How to Install & Run from GitHub)

Follow these simple steps if you are downloading this project from GitHub onto your computer:

### Step 1: Download the Project
You can either open your terminal and type this to clone the repository:
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd <YOUR_REPO_NAME>
```
*(Or simply click the green "Code" button on GitHub, select "Download ZIP", extract the folder to your computer, and open that folder in your terminal).*

### Step 2: Install Python
Make sure you have [Python](https://www.python.org/downloads/) installed on your computer. When installing Python (especially on Windows), make sure you check the box that says **"Add python.exe to PATH"**.

### Step 3: Install Required Libraries
This project relies on a few extra Python tools. Open your terminal (or Command Prompt) inside the downloaded project folder and run:
```bash
pip install -r requirements.txt
```
*(This command automatically installs `pandas`, `openpyxl`, `ddgs`, and `flask` for you).*

---

## 🛠️ How to Use the Script

You now have **two** ways to use this script: through a modern **HTML Visualizer (Web interface)**, or via the **Command Line**.

### Option 1: The HTML Visualizer (Recommended)
This gives you a beautifully formatted UI where you can just drag and drop files.

1. **Run the App**: Open your terminal and run:
   ```bash
   python app.py
   ```
2. **Open your Browser**: The terminal will print a link that looks like this: `http://127.0.0.1:5000`. Click it or copy it into Chrome, Edge, Safari, etc.
3. **Upload the file**: Click the box, select your `.xlsx` file, and hit "Start Search".
4. **Download**: Once it finishes, it will generate a new unique Excel file equipped with a timestamp (like `search_results_20260422_153022.xlsx`) and give you a download button right away!

### Option 2: The Command Line Route
If you enjoy the matrix hacker vibes.

1. **Run the script**: Open your terminal and run:
   ```bash
   python agent.py
   ```
2. **Follow the Prompt**: The script will instantly ask you: 
   `Enter the path to your input Excel file (e.g., sample_products.xlsx) [Press Enter for default]:`
   You can either type in the exact name of the file or just press **Enter** to default to `sample_products.xlsx`.
3. **Check your folder**: The script will run through all the files, pausing slightly between each request to avoid being blocked by search engines. Once done, a brand new file like `search_results_20260422_153022.xlsx` will appear in your project folder. No more accidentally overwriting older search histories!

*⚠️ IMPORTANT TIP: Make sure you DO NOT have the `search_results` file open in Microsoft Excel while the script is running. If the file is open, the script cannot save its new results and will crash with a "Permission denied" error.*

---

## 📊 Input Excel Sheet Format

For the script to understand your Excel sheet, the first row of your sheet MUST contain specific column names (exactly as written below, case-sensitive):

| GeM Product ID | GeM Title | GeM Brand | GeM Model |
| :--- | :--- | :--- | :--- |
| (Any ID number) | Acer Aspire Lite AL15 | Acer | AL15 52 |
| (Any ID number) | ProDot Toner Cartridge | ProDot | PLB-B021 |

**Why these exact names?** 
The script specifically looks for `GeM Title`, `GeM Brand`, and `GeM Model` to build its search. If your columns are named something else (like "Product Name" instead of "GeM Title"), the script won't know where to look. Other columns (like GeM Product ID) can be there, the script will just ignore them and pass them along to the final result file.

---

## 🌐 How to Add a New Website to Search

Right now, the script only looks for Amazon and Flipkart links. If you want to add another website (for example, **chroma.com** or **reliance.com**), you need to change **two lines of code** inside `agent.py`.

Open `agent.py` in your code editor and look for the `search_product` function at the top.

### **Change #1: Update the search query**
Find this line:
```python
query = f"{brand} {model} {title} amazon OR flipkart"
```
Change it to tell the search engine to also look for your new site. Just add an `OR` and your new website's name.
*Example:*
```python
query = f"{brand} {model} {title} amazon OR flipkart OR chroma"
```

### **Change #2: Update the link filter**
Find this line:
```python
if 'amazon.in' in link or 'flipkart.com' in link:
```
Change it to accept links that contain your new website's URL. 
*Example:*
```python
if 'amazon.in' in link or 'flipkart.com' in link or 'chroma.com' in link:
```

Save the file, and the next time you run it, the agent will also hunt for products on your newly added website!
