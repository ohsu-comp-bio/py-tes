<!-- markdownlint-disable -->

<a href="../../tes/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utils`
Exceptions and utilities. 


---

<a href="../../tes/utils.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `camel_to_snake`

```python
camel_to_snake(name: str) → str
```

Converts camelCase to snake_case. 



**Args:**
 
 - <b>`name`</b>:  String to convert. 



**Returns:**
 Converted string. 


---

<a href="../../tes/utils.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `unmarshal`

```python
unmarshal(j: Any, o: Type, convert_camel_case=True) → Any
```

Unmarshal a JSON string to a TES model. 



**Args:**
 
 - <b>`j`</b>:  JSON string or dictionary to unmarshal. 
 - <b>`o`</b>:  TES model to unmarshal to. 
 - <b>`convert_camel_case`</b>:  Convert values in `j` from camelCase to snake_case. 



**Returns:**
 Unmarshalled TES model. 



**Raises:**
 
 - <b>`UnmarshalError`</b>:  If `j` cannot be unmarshalled to `o`. 


---

<a href="../../tes/utils.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UnmarshalError`
Raised when a JSON string cannot be unmarshalled to a TES model. 

<a href="../../tes/utils.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(*args, **kwargs)
```









---

<a href="../../tes/utils.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TimeoutError`




<a href="../../tes/utils.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(*args, **kwargs)
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
