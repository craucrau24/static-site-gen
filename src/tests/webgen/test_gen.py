import unittest
from webgen.gen import extract_title

class TestGeneratorFunctions(unittest.TestCase):
    def test_extract_title_ok(self):
        text = "# Hello"
        self.assertEqual(extract_title(text), "Hello")

        text = "#   Hello world   "
        self.assertEqual(extract_title(text), "Hello world")

        text = """
[link](https://foobar.com/baz)
![image](https://foobar.com/baz.png)

# This is a heading

```
def dummy_function():
    print('Hello, world!')
```

        #### This is a second heading

1. First line
2. Second **line**

        """

        self.assertEqual(extract_title(text), "This is a heading")

    def test_extract_title_ko(self):
        text = """
[link](https://foobar.com/baz)
![image](https://foobar.com/baz.png)

## This is a heading

```
def dummy_function():
    print('Hello, world!')
```

        #### This is a second heading

1. First line
2. Second **line**

        """
        with self.assertRaises(Exception):
            extract_title(text)