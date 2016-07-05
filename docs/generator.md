[Back to Index](README.md)

# Generator

`generator.py` is a module which contains the `DataGenerator()` class. It is used in conjunction with an implementation of an Exporter and a JSON schema in order to generator random datasets.

--------

## Methods


### `generator.__init__(schema, seed="")`

The constructor method for the generator takes 2 arguments (minimum).

- `schema`

This is the path to the `*.json` file under the `conf/` directory where the schema for the generator is stored. It will only look under `conf/`

- `Exporter`

This should be an implementation of the Exporter superclass. This is necessary to get data from where it is generated to its desired format. Three (3) default exporters are provided with the repository. `csv`, `xml`, and `json`.

- `seed`

This is the seed for the random number generator. It is entirely optional and if the seed given is found to be a zero-length string then the seed used will be pseudo-randomly generated.

### `generator.generate()`

The `generate()` method takes no arguments and will produce a single line (entry) of data given the schema provided during instantiation.

The data produced will be in the format:

	{
		"field_name_1": field_value_1,
		"field_name_2": field_value_2,
		"field_name_3": field_value_3,
		....
	}


## Generator Configuration Reference

The data generator is driven by a JSON configuration. Each field for a generator row is driven by this configuration.

Initially, 4 (four) different types of values fields can be generated/mapped

- `string`
- `number`
- `boolean`
- `map`

We call each field or piece of data a **datum**. Each of these types has a subclass derived from the `AbstractDatum` class inside of `generator.py`.

To add more **datum**(data) in the future one would just need to create a new implementation from the `AbstractDatum` class

### Datum

Each field that can be generated is referred to as a **datum**. There are different types of datum and each require different configuration parameters.

Below is the documentation on the parameters required for each datum.

### **strings** - (`StringDatum`)

A string datum is denoted when the **type** property is set to `string`

	{
		"type": "string",
		"fieldName": "Sample_Field"
		....
	}

Required fields:

| Property Name | type |
|---------------|------|
| `fieldName` | `string` |
| `type` | `string` |
| `values` | `list` or `object` |

_A note on `values`_:

> The property `values` is where you give a list of strings which you want to be generated. If a list is given, then each string has _equal probability_ in being randomly selected. Otherwise, you can specify a JSON object which maps each desired string to a given probability. This will result in each string being randomly selected with the probability given. The probabilities must be between `0.0` and `1.0` add up to exactly `1.0` or else an error will be thrown

Samples:

	{
		"type": "string",
		"fieldName": "Sample_Field",
		"values": ["a", "b", "c", "d", "e"]
	}
	
The above demonstrates a string datum in which any value of `[a, b, c, d, e]` has equal probability of being generated.

	{
		"type": "string",
		"fieldName": "Sample_Field",
		"values": {
			"a": 0.5,
			"b": 0.1,
			"c": 0.05,
			"d": 0.15,
			"e": 0.2
		}
	}

In this example we see the values which are generated the same as the above example. However their **probabilities of being selected vary**.


### **Number** - (`IntDatum` or `DecimalDatum`)

A number datum is denoted when the **type** property is set to `int` or `decimal`

	{
		"type": "int", // or "decimal"
		"fieldName": "Sample_Field"
		....
	}

Required fields:

| Property Name | type |
|---------------|------|
| `fieldName` | `string` |
| `type` | `string` |
| `distribution` | `string` |

**`distribution`**

The distribution field is key here because it determines the other parameters you need to use generate values. Because we use the built-in python random number generator there are a number of functions which can generate different types of distributions. The number datum have access to the following distributions (with their respective arguments)

- **uniform(a, b)**
  - Defaults
    - `a`: 0
	- `b`: 1
- **exponential(lambda)**
  - Defaults
    - `lambda`: 1
- **gaussian(mu, sigma)**
  - Defaults
    - `mu`: 0
	- `sigma`: 1
- **gamma(alpha, beta)**
  - Defaults
    - `alpha`: 1
	- `beta`: 1

_For more information on python's `random` module [please refer to the documentation](https://docs.python.org/2/library/random.html)_.

Based on the type of distribution you should specify the corresponding parameters

Samples:

	{
		"type": "int",
		"fieldName": "Sample_Field",
		"distribution": "gaussian",
		"mu": 20,
		"sigma": 5
	}
	
The above demonstrates configuration of Gaussian distribution which produces integers that has a mean of ~20 and a standard deviation of 5.

	{
		"type": "decimal",
		"fieldName": "Sample_Field",
		"distribution": "exponential",
		"lambda": 0.5
	}

In this example we see an exponential distribution with a `lambda` parameter of `0.5` 


### **Boolean** - (`BooleanDatum`)

A boolean datum is denoted when the **type** property is set to `boolean`

	{
		"type": "boolean",
		"fieldName": "Sample_Field"
		....
	}

Required fields:

| Property Name | type |
|---------------|------|
| `fieldName` | `string` |
| `type` | `string` |

Due to the nature of having only being two possible options with boolean types as a default setting on this generator you can simply just define the `fieldName` and `type` (as boolean) and the generator will simply select True/False at a 50/50 probability.

However, if you'd like to tailor this to be different just use a JSON object key named `values` with the keys `True` and `False` mapped to respective probabilities (similar to the StringDatum). 

Again the probabilities **must** add up to `1.0`

Samples:

	{
		"type": "boolean",
		"fieldName": "Sample_Field"
	}
	
The above demonstrates configuration of boolean generator which produces True/False values with equal probabilities

	{
		"type": "boolean",
		"fieldName": "Sample_Field",
		"values": {
			"True": 0.2,
			"False": 0.8
		}
	}

In this example we see a boolean generator where `True` is generated 20% of the time and `False` is generated 80% of the time.


### **Map** - (`MapDatum`)

A map datum is denoted when the **type** property is set to `map`

	{
		"type": "map",
		"fieldName": "Sample_Field"
		....
	}

Required fields:

| Property Name | type |
|---------------|------|
| `fieldName` | `string` |
| `mapFromField` | `string` |
| `type` | `string` |
| `map` | `object` |

Sometimes you might want a column for different categories based on a field in the schema.

Example: You have a bunch of items being generated and each item falls into a certain category which you want to use as a field.

	{
		"ipod": "ELECTRONICS",
		"computer": "ELECTRONICS",
		"desk": "FURNITURE",
		"couch": "FURNITURE"
		...
	}

Samples:

	{
		"type": "map",
		"fieldName": "Sample_Mapped_Field",
		"mapFromField": "Sample_Field",
		"map": {
			"a": "vowel",
			"b": "consonant",
			"c": "consonant",
			"d": "consonant",
			"e": "vowel"
		}
	}
	

In this example we see a map generator where given different keys from the field named `Sample_Field` we create a new field called `Sample_Mapped_Field` which uses the corresponding values from the `map` object


### Sample Schemas


**Basic Sale Data**

	[
		{
			"type": "int",
			"fieldName": "price",
			"distribution": "gaussian"
			"mu": 50,
			"sigma": 20
		},
		{
			"type": "int",
			"fieldName": "store_number",
			"distribution": "gaussian"
			"mu": 10000,
			"sigma": 50
		},
		{
			"type": "boolean",
			"fieldName": "on_sale",
			"values": {
				"True": 0.23
				"False": 0.77
			}
		},
		{
			"type": "string",
			"fieldName": "service_rep",
			"values": ["Kate", "Billy", "John", "Michelle"]
		}
	]
		






