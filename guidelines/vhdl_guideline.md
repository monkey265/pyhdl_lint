# Implementation Status

| Rule | Rule Code | Implemented |
| --- | --- | --- |
| Entity name uppercase | VHDL-001 | [x] |
| Keywords ALL CAPS | VHDL-002 | [x] |
| Signals/Variables lowercase | VHDL-003 | [x] |
| Signal prefix `s_` | VHDL-004 | [x] |
| Variable prefix `v_` | VHDL-005 | [x] |
| Generic prefix `g_` | VHDL-006 | [x] |
| Process label required | VHDL-007 | [x] |
| Process label suffix `_proc` | VHDL-008 | [x] |
| Library `work` restricted | VHDL-009 | [x] |

# Basics

- Must is non negotiable
- Should and permitted is best practice
- Tip is recommended


- Keywords must be in all caps.
- Functions and procedures are permitted to be in lowercase.
- Signals and variables must be lowercase.
- Signals should have prefix `s_`
- Variables should have prefix `v_`
- STD and provided functions, procedures, typecasts etc. should be all caps, custom datatypes, procedures, functions can be lowercase.

- Created library must not be named work.
- IF/FOR/WHILE statements should be named.

# Port and generics
- Generics should have prefix `g_`
  - Example:

```vhdl
  GENERIC (
    g_num_tx   : INTEGER
  );
```

- Port should have comments that indicate categories like inputs/outputs/debug...

# Clock and reset

- Clock should be first specified port.
- Reset should be second specified port.
- Reset should have active value and synchronicity specified.
- Reset name should reflect synchronicity and active value.
- Reset should be active low.
- Example:
  - `areset_n/arst_n -> asynchronous reset negated`
  - `rst_n    -> synchronous reset negated` 
  

Example: 

```vhdl
PORT (
    -- Inputs
    clk_in      : IN STD_LOGIC;
    rst_n_in    : IN STD_LOGIC; -- synchronous reset, active low
    areset_n_in : IN STD_LOGIC  -- asynchronous reset, active low
);
```

# Process

- Process must be named.
- Name should be `something_proc`
- Example:

```vhdl
main_proc: PROCESS(clk_in)
BEGIN
    -- something
END PROCESS main_proc;
```

- Process with senstivity to only clock and reset should be in clocked modules.
- Process with sensitivity list ALL should be used for combinatorial modules.

```vhdl
reg_proc: PROCESS(clk_in, areset_n_in)
BEGIN
    reset_if: IF areset_n_in = '0' THEN
        -- Asynchronous Reset Logic
    ELSIF rising_edge(clk_in) THEN
        -- Synchronous Logic
    END IF reset_if;
END PROCESS reg_proc;
```

## Combinatorial process

- Combinatorial process must have ALL sensitivity - `PROCESS(ALL)`
- If you are using VHDL 93, sensitivity list must contain every signal read inside the process.

### Latch prevention

- To ensure the logic is purely combinational and not a latch, every signal assigned in the process must be assigned a value in all possible branches (i.e., every IF needs an ELSE, every CASE needs a WHEN OTHERS)

# Architecture

# FSM

## Process structure

### Two-Process FSM

### One-Process FSM
- Reccomended on FPGA

## State changes

- Never use rising_edge() on input signals (data) to control state changes.
- If an edge trigger is required, generate a pulse signal (lasts one clock cycle) and check the level of that pulse.
- When specifing state transitions via IF case, do not specify else cause, leave only plain if. Synthetiser will complain.

# Appendix

## Attributes

An attribute provides additional information about a specific part of a VHDL description, such as a type, range, signal, or function. Predefined attributes can return constants, functions, signals, or ranges.

While the VHDL standard defines a robust set of predefined attributes (listed below), users can also define their own (see *Attributes (User-Defined)*).

### Syntax

```vhdl
object_name[ signature ]'attribute_name[ ( expression ) ]
-- signature = [ type_name, ... ] return type_name

```

---

## 1. Global Type Attributes

Each type or subtype `T` has a basic attribute indicating its base type. This is primarily used as a prefix for other attributes.

| Attribute | Result |
| --- | --- |
| `T'Base` | Returns the base type of `T`. |

---

## 2. Scalar Type Attributes

These attributes return bounds and string representations of scalar types.

| Attribute | Return Type | Description |
| --- | --- | --- |
| `T'Left` | Same as `T` | The leftmost value of `T`. |
| `T'Right` | Same as `T` | The rightmost value of `T`. |
| `T'Low` | Same as `T` | The least value in `T`. |
| `T'High` | Same as `T` | The greatest value in `T`. |
| `T'Ascending` | `Boolean` | `True` if `T` is an ascending range, `False` otherwise. |
| `T'Image(x)` | `String` | A textual representation of value `x`. |
| `T'Value(s)` | Base of `T` | The value in `T` represented by string `s`. |

---

## 3. Discrete/Physical Type Attributes

These attributes facilitate navigation through discrete or physical types (e.g., integers, enumerations).

| Attribute | Return Type | Description |
| --- | --- | --- |
| `T'Pos(s)` | `Integer` | Position number of `s` in `T`. |
| `T'Val(x)` | Base of `T` | Value at integer position `x` in `T`. |
| `T'Succ(s)` | Base of `T` | Value at position one greater than `s`. |
| `T'Pred(s)` | Base of `T` | Value at position one less than `s`. |
| `T'Leftof(s)` | Base of `T` | Value at position one to the left of `s`. |
| `T'Rightof(s)` | Base of `T` | Value at position one to the right of `s`. |

> **Note:** Synthesis tools generally discourage the use of `Pos`, `Val`, `Succ`, `Pred`, `Leftof`, and `Rightof` for hardware generation.

---

## 4. Array Attributes

These attributes are essential for writing generic, reusable code that adapts to arrays of any size.

| Attribute | Result |
| --- | --- |
| `A'Left(n)` | Leftmost value in index range of dimension `n`. |
| `A'Right(n)` | Rightmost value in index range of dimension `n`. |
| `A'Low(n)` | Lower bound of index range of dimension `n`. |
| `A'High(n)` | Upper bound of index range of dimension `n`. |
| `A'Range(n)` | The specific index range of dimension `n` (e.g., `7 downto 0`). |
| `A'Reverse_range(n)` | The reversed index range of dimension `n` (e.g., `0 to 7`). |
| `A'Length(n)` | Number of values in the `n`-th index range. |
| `A'Ascending(n)` | `True` if index range is ascending (`to`), `False` otherwise (`downto`). |

---

## 5. Signal Attributes

Signal attributes are used heavily in simulation models and behavioral verification. Some (like `'Event` and `'Stable`) are crucial for detecting edges or implementing timing checks.

| Attribute | Result |
| --- | --- |
| `S'Delayed(t)` | Signal `S` delayed by `t` time units. |
| `S'Stable(t)` | `True` if no event has occurred on `S` for `t` time units. |
| `S'Quiet(t)` | `True` if no *transaction* (assignment) has occurred on `S` for `t` time units. |
| `S'Transaction` | A `Bit` signal that toggles in every cycle where a transaction occurs on `S`. |
| `S'Event` | `True` if an event (value change) occurred on `S` in the current cycle. |
| `S'Active` | `True` if a transaction (assignment, even if value is same) occurred on `S` in the current cycle. |
| `S'Last_event` | Time elapsed since the last event on `S`. |
| `S'Last_active` | Time elapsed since the last transaction on `S`. |
| `S'Last_value` | The previous value of `S` before the last event. |
| `S'Driving` | `True` if the current process is driving `S`. |
| `S'Driving_value` | The value currently being driven onto `S` by the enclosing process. |

---

- When used inside GENERATE statement, be careful about static signal prefix. Especially when using attribute on arrays. You wont be able to check events of individual array components but just whole array.

## 6. Named Entity Attributes

Useful for reporting, assertions, and logging, allowing messages to pinpoint specific hierarchy paths.

| Attribute | Result |
| --- | --- |
| `E'Simple_name` | String of the simple name defined in the declaration of `E`. |
| `E'Path_name` | String describing the full hierarchy path to `E`. |
| `E'Instance_name` | Similar to `Path_name` but includes entity/architecture names for every component instance in the path. |

---

## Examples

**Scalar Types:**

```vhdl
type T is (low, middle, high); 
-- T'Left  = low
-- T'Right = high

```

**Arrays:**

```vhdl
signal S: std_logic_vector(3 downto 0);
-- S'Range   = 3 downto 0
-- S'Length  = 4
-- S'High    = 3
-- S'Low     = 0

```

**Synthesis Note:**
Attributes of enumeration types, as well as navigation attributes (`Pos`, `Val`, `Succ`, etc.), should generally be avoided in synthesizable RTL code.

