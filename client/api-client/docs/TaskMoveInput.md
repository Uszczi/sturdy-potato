# TaskMoveInput

## Properties

| Name       | Type                        |
| ---------- | --------------------------- |
| `status`   | [TaskStatus](TaskStatus.md) |
| `position` | number                      |

## Example

```typescript
import type { TaskMoveInput } from "";

// TODO: Update the object below with actual values
const example = {
  status: null,
  position: null,
} satisfies TaskMoveInput;

console.log(example);

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example);
console.log(exampleJSON);

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TaskMoveInput;
console.log(exampleParsed);
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
