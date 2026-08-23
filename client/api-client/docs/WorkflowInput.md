
# WorkflowInput

The complete desired workflow for one board.  Beyond field shapes, the rules that make a workflow valid (how many statuses, exactly one initial, at least one terminal) live in the domain, so a bad workflow fails the same way whether it arrives over HTTP or from the CLI.

## Properties

Name | Type
------------ | -------------
`statuses` | [Array&lt;StatusInput&gt;](StatusInput.md)
`reassign` | { [key: string]: string; }

## Example

```typescript
import type { WorkflowInput } from ''

// TODO: Update the object below with actual values
const example = {
  "statuses": null,
  "reassign": null,
} satisfies WorkflowInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as WorkflowInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


