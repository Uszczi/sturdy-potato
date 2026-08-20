
# TaskCreateInput


## Properties

Name | Type
------------ | -------------
`title` | string
`description` | string
`completed` | boolean
`projectId` | number
`dueDate` | Date

## Example

```typescript
import type { TaskCreateInput } from ''

// TODO: Update the object below with actual values
const example = {
  "title": null,
  "description": null,
  "completed": null,
  "projectId": null,
  "dueDate": null,
} satisfies TaskCreateInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TaskCreateInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


