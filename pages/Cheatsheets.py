import streamlit as st
from utils.db import get_supabase
st.set_page_config(page_title="Cheatsheets", page_icon="📄", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .cheatsheet-header {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        padding: 1.5rem 2rem; border-radius: 14px; color: white;
        margin-bottom: 1.5rem;
    }
    .cheatsheet-card {
        background: white; border-radius: 12px;
        padding: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e0e7ff;
    }
    pre {
        background: #1e1e1e !important;
        color: #d4d4d4 !important;
        border-radius: 8px !important;
        padding: 14px !important;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# ─── Auth Guard ────────────────────────────────────────
if "student" not in st.session_state or st.session_state.student is None:
    st.warning("Please login from the main page.")
    st.stop()

student = st.session_state.student
sb = get_supabase()
enrolled = student.get("enrolled_subjects", [])

st.title("📄 Cheatsheets")

if not enrolled:
    st.warning("Please enroll in a subject first from **My Subjects**.")
    st.stop()

# ─── Selectors ─────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    subject_choice = st.selectbox("📚 Select Subject", enrolled)
with col2:
    subj = sb.table("subjects").select("*").eq("name", subject_choice).execute()
    if not subj.data:
        st.stop()
    topics = sb.table("topics").select("*").eq(
        "subject_id", subj.data[0]["id"]).order("order_index").execute()
    selected_topic_name = st.selectbox("📌 Select Topic", [t["title"] for t in topics.data])

topic = next((t for t in topics.data if t["title"] == selected_topic_name), None)
if not topic:
    st.stop()

# ─── Header ────────────────────────────────────────────
s = subj.data[0]
st.markdown(f"""
<div class="cheatsheet-header">
    <h2>{s['icon']} {s['name']} — {selected_topic_name}</h2>
    <p style="opacity:0.9;">Quick reference cheatsheet</p>
</div>
""", unsafe_allow_html=True)

# ─── Built-in Cheatsheets ──────────────────────────────
CHEATSHEETS = {
    "Python": {
        "Introduction to Python": """
## 🐍 Python Basics Cheatsheet

### Variables & Data Types
```python
age = 25              # int
price = 19.99         # float
name = "Alice"        # str
is_active = True      # bool
nothing = None        # NoneType

print(type(age))      # <class 'int'>
```

### Input & Output
```python
name = input("Enter your name: ")
print("Hello,", name)
print(f"Hello, {name}!")         # f-string (recommended)
print("Score:", 95, sep=" -> ")  # custom separator
```

### Type Conversion
```python
x = int("42")         # str -> int
y = float("3.14")     # str -> float
z = str(100)          # int -> str
b = bool(0)           # int -> bool (0=False, else True)
```

### Arithmetic Operators
```python
10 + 3   # 13  (addition)
10 - 3   # 7   (subtraction)
10 * 3   # 30  (multiplication)
10 / 3   # 3.33 (division)
10 // 3  # 3   (floor division)
10 % 3   # 1   (modulo)
10 ** 3  # 1000 (power)
```

### String Operations
```python
s = "Hello, World!"
len(s)            # 13
s.upper()         # HELLO, WORLD!
s.lower()         # hello, world!
s.strip()         # removes whitespace
s.split(",")      # ['Hello', ' World!']
s.replace("World", "Python")
s[0:5]            # Hello (slicing)
s[::-1]           # reverse string
f"{name} is {age} years old"
```
        """,

        "Control Flow": """
## 🔀 Control Flow Cheatsheet

### If / Elif / Else
```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(grade)  # B
```

### Ternary (One-line If)
```python
result = "Pass" if score >= 50 else "Fail"
```

### For Loop
```python
for i in range(5):        # 0,1,2,3,4
    print(i)

for i in range(1, 6):     # 1,2,3,4,5
    print(i)

for i in range(0, 10, 2): # 0,2,4,6,8
    print(i)

for ch in "Hello":        # iterate string
    print(ch)

for i, val in enumerate(["a","b","c"]):
    print(i, val)          # 0 a, 1 b, 2 c
```

### While Loop
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### Loop Control
```python
for i in range(10):
    if i == 3:
        continue    # skip this iteration
    if i == 7:
        break       # exit loop
    print(i)

for i in range(3):
    print(i)
else:
    print("Loop finished!")  # runs if no break
```

### Comparison & Logical Operators
```python
==  !=  >  <  >=  <=    # comparison
and  or  not              # logical
x in [1,2,3]             # membership
x is None                 # identity
```
        """,

        "Functions": """
## 🔧 Functions Cheatsheet

### Basic Function
```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Alice")
print(message)
```

### Default Parameters
```python
def greet(name, msg="Hello"):
    return f"{msg}, {name}!"

greet("Alice")           # Hello, Alice!
greet("Bob", "Hi")       # Hi, Bob!
```

### Multiple Return Values
```python
def min_max(lst):
    return min(lst), max(lst)

lo, hi = min_max([3,1,4,1,5])
print(lo, hi)   # 1 5
```

### *args (Variable Positional)
```python
def total(*args):
    return sum(args)

total(1, 2, 3, 4)   # 10
```

### **kwargs (Variable Keyword)
```python
def display(**kwargs):
    for key, val in kwargs.items():
        print(f"{key}: {val}")

display(name="Alice", age=25)
```

### Lambda Functions
```python
square  = lambda x: x ** 2
add     = lambda a, b: a + b
is_even = lambda n: n % 2 == 0

nums = [3,1,4,1,5]
sorted_nums = sorted(nums, key=lambda x: -x)
```

### Scope
```python
x = 10              # global

def change():
    global x
    x = 20          # modifies global

def show():
    y = 5           # local only
```
        """,

        "Data Structures": """
## 📦 Data Structures Cheatsheet

### Lists
```python
lst = [1, 2, 3, 4, 5]

# Add
lst.append(6)           # [1,2,3,4,5,6]
lst.insert(0, 0)        # [0,1,2,3,4,5,6]
lst.extend([7, 8])      # add multiple

# Remove
lst.remove(3)           # removes first 3
lst.pop()               # removes last
lst.pop(0)              # removes at index

# Search & Sort
lst.index(4)            # position of 4
lst.count(1)            # count of 1s
lst.sort()              # ascending
lst.sort(reverse=True)  # descending
lst.reverse()           # in-place reverse
sorted(lst)             # returns new sorted list

# Slicing
lst[1:4]    # elements 1,2,3
lst[:3]     # first 3
lst[-2:]    # last 2
lst[::2]    # every other

# List Comprehension
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x%2==0]
```

### Dictionaries
```python
d = {"name": "Alice", "age": 25, "city": "NYC"}

# Access
d["name"]             # Alice
d.get("phone", "N/A") # safe access with default

# Add / Update
d["email"] = "a@b.com"
d.update({"age": 26, "country": "US"})

# Delete
del d["city"]
d.pop("age")

# Iterate
for k in d.keys():   print(k)
for v in d.values(): print(v)
for k,v in d.items(): print(k, v)

# Dict comprehension
squares = {x: x**2 for x in range(5)}
```

### Sets
```python
s = {1, 2, 3, 4}        # no duplicates!

s.add(5)
s.remove(2)             # raises error if missing
s.discard(99)           # safe remove

s1 = {1,2,3}
s2 = {2,3,4}
s1 | s2   # union:        {1,2,3,4}
s1 & s2   # intersection: {2,3}
s1 - s2   # difference:   {1}
s1 ^ s2   # symmetric diff: {1,4}
```

### Tuples
```python
t = (1, 2, 3)       # immutable!
t[0]                # 1
a, b, c = t         # unpacking
t.count(1)          # count occurrences
t.index(2)          # find position
```
        """,

        "File Handling": """
## 📁 File Handling Cheatsheet

### Read a File
```python
# Method 1: read all at once
with open("file.txt", "r") as f:
    content = f.read()

# Method 2: read line by line
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())

# Method 3: read into list
with open("file.txt", "r") as f:
    lines = f.readlines()
```

### Write to a File
```python
# Write (overwrites existing)
with open("output.txt", "w") as f:
    f.write("Hello, World!\\n")

# Append
with open("log.txt", "a") as f:
    f.write("New log entry\\n")
```

### File Modes
```python
"r"   # read (default)
"w"   # write (create/overwrite)
"a"   # append
"r+"  # read and write
"rb"  # read binary
"wb"  # write binary
```

### Exception Handling
```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except (TypeError, ValueError) as e:
    print(f"Type or Value error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
else:
    print("No error!")       # runs if no exception
finally:
    print("Always runs")     # cleanup code
```

### Custom Exceptions
```python
class MyError(Exception):
    def __init__(self, message):
        super().__init__(message)

raise MyError("Something went wrong!")
```
        """,

        "OOP in Python": """
## 🏗 OOP in Python Cheatsheet

### Class Basics
```python
class Animal:
    species = "Unknown"     # class variable
    
    def __init__(self, name, age):
        self.name = name    # instance variables
        self.age = age
    
    def speak(self):
        return f"{self.name} makes a sound"
    
    def __str__(self):
        return f"Animal({self.name}, {self.age})"
    
    @classmethod
    def get_species(cls):
        return cls.species
    
    @staticmethod
    def is_alive():
        return True

a = Animal("Buddy", 3)
print(a.speak())
print(str(a))
```

### Inheritance
```python
class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)   # call parent
        self.breed = breed
    
    def speak(self):                  # override
        return f"{self.name} says Woof!"
    
    def fetch(self):
        return f"{self.name} fetches the ball"

dog = Dog("Max", 2, "Labrador")
print(dog.speak())
print(isinstance(dog, Animal))    # True
```

### Encapsulation
```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance    # private (__)
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
    
    def get_balance(self):
        return self.__balance

acc = BankAccount(1000)
acc.deposit(500)
print(acc.get_balance())   # 1500
```

### Magic Methods
```python
__init__    # constructor
__str__     # string representation
__repr__    # developer representation
__len__     # len()
__eq__      # ==
__lt__      # <
__add__     # +
__getitem__ # []
```
        """,

        "Modules & Libraries": """
## 📦 Modules & Libraries Cheatsheet

### Import Styles
```python
import math
import math as m
from math import sqrt, pi
from math import *           # not recommended

# Custom module
from mymodule import my_function
```

### math module
```python
import math
math.sqrt(16)       # 4.0
math.pow(2, 10)     # 1024.0
math.ceil(4.2)      # 5
math.floor(4.8)     # 4
math.log(100, 10)   # 2.0
math.pi             # 3.14159...
math.e              # 2.71828...
math.factorial(5)   # 120
```

### os module
```python
import os
os.getcwd()                   # current directory
os.listdir(".")               # list files
os.mkdir("new_folder")        # create folder
os.path.exists("file.txt")    # check existence
os.path.join("dir","file.txt")# path join
os.environ.get("HOME")        # env variable
```

### datetime module
```python
from datetime import datetime, date, timedelta

now = datetime.now()
today = date.today()
print(now.strftime("%Y-%m-%d %H:%M:%S"))

delta = timedelta(days=7)
next_week = today + delta
```

### random module
```python
import random
random.randint(1, 100)        # random int
random.random()               # 0.0 - 1.0
random.choice([1,2,3])        # random element
random.shuffle(my_list)       # shuffle in-place
random.sample(my_list, 3)     # 3 unique random items
```

### sys module
```python
import sys
sys.argv           # command line args
sys.exit(0)        # exit program
sys.path           # module search path
sys.version        # Python version
```
        """,

        "Projects & Practice": """
## 🚀 Projects & Problem Solving Cheatsheet

### Common Patterns

#### Fibonacci
```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        print(a, end=" ")
        a, b = b, a + b
```

#### Prime Check
```python
def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True
```

#### Palindrome Check
```python
def is_palindrome(s):
    s = s.lower().replace(" ","")
    return s == s[::-1]
```

#### Factorial (Recursion)
```python
def factorial(n):
    if n == 0: return 1
    return n * factorial(n - 1)
```

#### Anagram Check
```python
def is_anagram(s1, s2):
    return sorted(s1.lower()) == sorted(s2.lower())
```

### Tips for Problem Solving
- **Read** the problem carefully — note input/output format
- **Examples** — trace through sample cases by hand
- **Edge cases** — empty input, zero, negative numbers
- **Plan** — write pseudocode before coding
- **Test** — check your solution with all sample test cases
- **Optimize** — think about time & space complexity
        """
    },

    "C++": {
        "C++ Basics": """
## ⚡ C++ Basics Cheatsheet

### Hello World
```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
```

### Variables & Data Types
```cpp
int    age     = 25;
float  price   = 19.99f;
double pi      = 3.14159265;
char   grade   = 'A';
bool   active  = true;
string name    = "Alice";   // needs #include <string>

// Constants
const int MAX = 100;
```

### Input & Output
```cpp
#include <iostream>
using namespace std;

int num;
string word;

cin >> num;          // read int
cin >> word;         // read word (stops at space)
getline(cin, line);  // read full line

cout << "Value: " << num << endl;
cout << fixed << setprecision(2) << 3.14159;  // formatted
```

### Type Casting
```cpp
int x = (int) 3.99;        // 3
double d = (double) 5 / 2; // 2.5
int y = static_cast<int>(3.7); // 3 (preferred)
```

### Operators
```cpp
+  -  *  /  %           // arithmetic
++  --                   // increment/decrement
==  !=  >  <  >=  <=    // comparison
&&  ||  !                // logical
&  |  ^  ~  <<  >>      // bitwise
```
        """,

        "Control Structures": """
## 🔀 C++ Control Structures Cheatsheet

### If / Else If / Else
```cpp
int score = 85;

if (score >= 90) {
    cout << "A";
} else if (score >= 80) {
    cout << "B";
} else if (score >= 70) {
    cout << "C";
} else {
    cout << "F";
}

// Ternary
string result = (score >= 50) ? "Pass" : "Fail";
```

### Switch
```cpp
char grade = 'B';
switch (grade) {
    case 'A': cout << "Excellent"; break;
    case 'B': cout << "Good";      break;
    case 'C': cout << "Average";   break;
    default:  cout << "Invalid";
}
```

### For Loop
```cpp
for (int i = 0; i < 5; i++) {
    cout << i << " ";
}

// Range-based for (C++11+)
int arr[] = {1, 2, 3, 4, 5};
for (int x : arr) {
    cout << x << " ";
}
```

### While & Do-While
```cpp
// While
int i = 0;
while (i < 5) {
    cout << i++;
}

// Do-while (runs at least once)
int n;
do {
    cin >> n;
} while (n <= 0);
```

### Break & Continue
```cpp
for (int i = 0; i < 10; i++) {
    if (i == 3) continue;   // skip 3
    if (i == 7) break;      // stop at 7
    cout << i << " ";
}
```
        """,

        "Functions & Arrays": """
## 🔧 Functions & Arrays Cheatsheet

### Functions
```cpp
// Declaration
int add(int a, int b);

// Definition
int add(int a, int b) {
    return a + b;
}

// Default parameters
void greet(string name, string msg = "Hello") {
    cout << msg << ", " << name << "!" << endl;
}

// Pass by value vs reference
void byValue(int x) { x = 100; }        // no effect outside
void byRef(int& x)  { x = 100; }        // modifies original
void byPtr(int* x)  { *x = 100; }       // modifies original
```

### Function Overloading
```cpp
int    area(int side)         { return side * side; }
double area(double r)         { return 3.14 * r * r; }
int    area(int l, int w)     { return l * w; }
```

### 1D Arrays
```cpp
int arr[5] = {1, 2, 3, 4, 5};
int zeros[10] = {};             // all zeros

arr[0] = 10;                    // access/modify
int n = sizeof(arr)/sizeof(arr[0]);  // length

// Pass array to function
void printArr(int arr[], int n) {
    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";
}
```

### 2D Arrays
```cpp
int matrix[3][3] = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};

for (int i = 0; i < 3; i++)
    for (int j = 0; j < 3; j++)
        cout << matrix[i][j] << " ";
```

### Strings in C++
```cpp
#include <string>
string s = "Hello, World!";

s.length()          // 13
s.size()            // 13
s.substr(0, 5)      // Hello
s.find("World")     // 7
s.replace(7,5,"C++")
s += " How are you?"
s.empty()           // false
s[0]                // 'H'
```
        """,

        "Pointers & References": """
## 🔗 Pointers & References Cheatsheet

### Pointer Basics
```cpp
int x = 10;
int* ptr = &x;          // ptr holds address of x

cout << x;              // 10 (value)
cout << &x;             // address of x
cout << ptr;            // address (same as &x)
cout << *ptr;           // 10 (dereference)

*ptr = 50;              // changes x to 50
```

### Pointer Arithmetic
```cpp
int arr[] = {10, 20, 30, 40, 50};
int* p = arr;           // points to arr[0]

cout << *p;             // 10
cout << *(p+1);         // 20
cout << *(p+2);         // 30
p++;                    // now points to arr[1]
```

### References
```cpp
int x = 10;
int& ref = x;           // ref is alias for x

ref = 50;               // x is now 50
cout << x;              // 50

// References MUST be initialized
// int& r;  // ERROR!
```

### Dynamic Memory
```cpp
// Allocate single variable
int* p = new int;
*p = 42;
delete p;               // free memory

// Allocate array
int* arr = new int[10];
arr[0] = 1;
delete[] arr;           // free array

// With initialization
int* p2 = new int(100); // *p2 = 100
```

### Null Pointer
```cpp
int* p = nullptr;       // C++11 (preferred)
int* q = NULL;          // older style

if (p != nullptr) {
    // safe to dereference
}
```

### Pointer vs Reference
```cpp
// Pointer: can be null, can be reassigned
// Reference: must be initialized, cannot be reassigned

void swap_ptr(int* a, int* b) {
    int temp = *a; *a = *b; *b = temp;
}
void swap_ref(int& a, int& b) {
    int temp = a; a = b; b = temp;
}

swap_ptr(&x, &y);   // call with &
swap_ref(x, y);     // call directly
```
        """,

        "OOP in C++": """
## 🏗 OOP in C++ Cheatsheet

### Class Basics
```cpp
class Animal {
private:
    string name;
    int age;

public:
    // Constructor
    Animal(string n, int a) : name(n), age(a) {}
    
    // Destructor
    ~Animal() {}
    
    // Getters / Setters
    string getName() { return name; }
    void setAge(int a) { age = a; }
    
    // Method
    virtual void speak() {
        cout << name << " makes a sound" << endl;
    }
    
    // Overload <<
    friend ostream& operator<<(ostream& os, Animal& a) {
        os << "Animal(" << a.name << ")";
        return os;
    }
};
```

### Inheritance
```cpp
class Dog : public Animal {
private:
    string breed;
public:
    Dog(string n, int a, string b) 
        : Animal(n, a), breed(b) {}
    
    void speak() override {
        cout << getName() << " says Woof!" << endl;
    }
};

Dog d("Max", 2, "Lab");
d.speak();                    // Max says Woof!
Animal* ptr = &d;
ptr->speak();                 // polymorphism!
```

### Access Specifiers
```cpp
public:    // accessible anywhere
private:   // only within class
protected: // within class and subclasses
```

### Abstract Class
```cpp
class Shape {
public:
    virtual double area() = 0;    // pure virtual
    virtual void display() {
        cout << "Area: " << area();
    }
};

class Circle : public Shape {
    double r;
public:
    Circle(double r) : r(r) {}
    double area() override { return 3.14 * r * r; }
};
```
        """,

        "STL - Standard Template Library": """
## 📚 STL Cheatsheet

### Vector
```cpp
#include <vector>

vector<int> v = {3, 1, 4, 1, 5};
v.push_back(9);          // add end
v.pop_back();            // remove end
v.insert(v.begin(), 0);  // insert at front
v.erase(v.begin());      // remove first
v.size();                // number of elements
v.empty();               // true if empty
v[0];                    // access (no bounds check)
v.at(0);                 // access (bounds check)
v.front(); v.back();     // first/last element
```

### Map (Ordered)
```cpp
#include <map>

map<string, int> scores;
scores["Alice"] = 95;
scores["Bob"]   = 87;

scores.count("Alice");   // 1 if exists
scores.find("Bob");      // iterator
scores.erase("Bob");
scores.size();

for (auto& [key, val] : scores)
    cout << key << ": " << val << "\\n";
```

### Unordered Map (Hash Map)
```cpp
#include <unordered_map>
unordered_map<string, int> umap;
// O(1) average access vs O(log n) for map
```

### Set
```cpp
#include <set>
set<int> s = {5, 3, 1, 4, 2};  // auto-sorted, unique

s.insert(6);
s.erase(3);
s.count(4);   // 1 if exists, 0 if not
s.size();

for (int x : s) cout << x << " ";  // 1 2 4 5 6
```

### Queue & Stack
```cpp
#include <queue>
queue<int> q;
q.push(1); q.push(2);
q.front(); q.pop();     // FIFO

#include <stack>
stack<int> stk;
stk.push(1); stk.push(2);
stk.top(); stk.pop();   // LIFO
```

### Algorithms
```cpp
#include <algorithm>

sort(v.begin(), v.end());                    // ascending
sort(v.begin(), v.end(), greater<int>());    // descending
sort(v.begin(), v.end(), [](int a, int b){ return a > b; });

reverse(v.begin(), v.end());
auto it = find(v.begin(), v.end(), 5);
int mn = *min_element(v.begin(), v.end());
int mx = *max_element(v.begin(), v.end());
int total = accumulate(v.begin(), v.end(), 0);
bool found = binary_search(v.begin(), v.end(), 3);
```
        """,

        "File Handling & Exceptions": """
## 📁 File Handling & Exceptions Cheatsheet

### Writing to File
```cpp
#include <fstream>

ofstream outFile("output.txt");
if (outFile.is_open()) {
    outFile << "Hello, File!" << endl;
    outFile << 42 << endl;
    outFile.close();
}

// Append mode
ofstream log("log.txt", ios::app);
log << "New entry\\n";
```

### Reading from File
```cpp
ifstream inFile("data.txt");
if (inFile.is_open()) {
    string line;
    while (getline(inFile, line)) {
        cout << line << endl;
    }
    inFile.close();
}

// Read word by word
int num;
while (inFile >> num) {
    cout << num << " ";
}
```

### File Modes
```cpp
ios::in       // read
ios::out      // write
ios::app      // append
ios::binary   // binary mode
ios::trunc    // truncate (default with out)
ios::ate      // seek to end after open

// Combined
fstream f("file.txt", ios::in | ios::out);
```

### Exception Handling
```cpp
#include <stdexcept>

try {
    int x = 0;
    if (x == 0)
        throw runtime_error("Division by zero!");
    int result = 10 / x;
}
catch (const runtime_error& e) {
    cerr << "Runtime error: " << e.what() << endl;
}
catch (const exception& e) {
    cerr << "Exception: " << e.what() << endl;
}
catch (...) {
    cerr << "Unknown exception!" << endl;
}
finally {
    // C++ doesn't have finally; use RAII pattern
}
```

### Custom Exception
```cpp
class MyException : public exception {
    string msg;
public:
    MyException(string m) : msg(m) {}
    const char* what() const noexcept override {
        return msg.c_str();
    }
};

throw MyException("Custom error occurred");
```
        """,

        "Competitive Programming": """
## 🏆 Competitive Programming Cheatsheet

### Fast I/O
```cpp
ios_base::sync_with_stdio(false);
cin.tie(NULL);
```

### Common Patterns

#### Check Prime
```cpp
bool isPrime(int n) {
    if (n < 2) return false;
    for (int i = 2; i * i <= n; i++)
        if (n % i == 0) return false;
    return true;
}
```

#### GCD & LCM
```cpp
#include <algorithm>
int g = __gcd(a, b);
int l = (a / g) * b;    // prevent overflow
```

#### Sieve of Eratosthenes
```cpp
vector<bool> sieve(int n) {
    vector<bool> is_prime(n+1, true);
    is_prime[0] = is_prime[1] = false;
    for (int i = 2; i*i <= n; i++)
        if (is_prime[i])
            for (int j = i*i; j <= n; j += i)
                is_prime[j] = false;
    return is_prime;
}
```

#### Binary Search
```cpp
int binarySearch(vector<int>& arr, int target) {
    int lo = 0, hi = arr.size() - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

#### Prefix Sum
```cpp
vector<int> prefix(n+1, 0);
for (int i = 0; i < n; i++)
    prefix[i+1] = prefix[i] + arr[i];

// Sum from l to r (0-indexed):
int rangeSum = prefix[r+1] - prefix[l];
```

### Useful Macros
```cpp
#define ll  long long
#define pb  push_back
#define mp  make_pair
#define all(x) x.begin(), x.end()
#define INF 1e18

typedef pair<int,int> pii;
typedef vector<int>   vi;
```
        """
    }
}

# ─── Display Cheatsheet ────────────────────────────────
cheatsheets = sb.table("cheatsheets").select("*").eq(
    "topic_id", topic["id"]).execute()

if cheatsheets.data:
    # DB cheatsheets take priority
    for c in cheatsheets.data:
        st.markdown(f"### 📄 {c['title']}")
        st.markdown(c["content"])
elif subject_choice in CHEATSHEETS and selected_topic_name in CHEATSHEETS[subject_choice]:
    st.markdown("""
    <div class="cheatsheet-card">
    """, unsafe_allow_html=True)
    st.markdown(CHEATSHEETS[subject_choice][selected_topic_name])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Download button
    cheatsheet_text = CHEATSHEETS[subject_choice][selected_topic_name]
    st.download_button(
        "⬇️ Download Cheatsheet",
        data=cheatsheet_text,
        file_name=f"{subject_choice}_{selected_topic_name.replace(' ','_')}_cheatsheet.md",
        mime="text/markdown"
    )
else:
    st.info(f"Cheatsheet for **{selected_topic_name}** coming soon!")
    st.markdown("Admin can add custom cheatsheets via the Supabase `cheatsheets` table.")