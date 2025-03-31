def zero_division_error():
    x = 1 / 0  

def key_error():
    d = {"name": "Alice"}
    print(d["age"])  

def index_error():
    lst = [1, 2, 3]
    print(lst[5]) 

def attribute_error():
    x = None
    x.append(5) 

def type_error():
    x = 5 + "hello" 

def recursion_error():
    def recurse():
        recurse()
    recurse()

def tensorflow_shape_mismatch():
    import tensorflow as tf
    a = tf.constant([1, 2, 3])
    b = tf.constant([[1], [2], [3]])
    c = a + b 

def pytorch_shape_mismatch():
    import torch
    a = torch.tensor([1, 2, 3])
    b = torch.tensor([[1], [2], [3]])
    c = a + bytearray

def pytorch_invalid_shape():
    import torch
    a = torch.tensor([[1, 2, 3], [4, 5]])

error_functions = {
    "ZeroDivisionError": zero_division_error,
    "KeyError": key_error,
    "IndexError": index_error,
    "AttributeError": attribute_error,
    "TypeError": type_error,
    "RecursionError": recursion_error,
    "InvalidArgumentError (TensorFlow)": tensorflow_shape_mismatch,
    "RuntimeError (PyTorch)": pytorch_shape_mismatch,
    "ValueError (PyTorch)": pytorch_invalid_shape,
}
