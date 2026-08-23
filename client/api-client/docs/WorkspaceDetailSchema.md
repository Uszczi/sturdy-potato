
# WorkspaceDetailSchema

One workspace, with the workflow the inbox board renders as columns.  It is also the template every new project\'s workflow is copied from.

## Properties

Name | Type
------------ | -------------
`workflow` | [Array&lt;StatusSchema&gt;](StatusSchema.md)
`id` | number
`name` | string
`isPersonal` | boolean
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { WorkspaceDetailSchema } from ''

// TODO: Update the object below with actual values
const example = {
  "workflow": null,
  "id": null,
  "name": null,
  "isPersonal": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies WorkspaceDetailSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as WorkspaceDetailSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


