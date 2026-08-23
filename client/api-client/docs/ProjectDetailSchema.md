
# ProjectDetailSchema

One project, with the workflow its board renders as columns.  Only the detail response carries it: the sidebar lists projects but never draws their boards, so shipping every workflow there would be dead weight.

## Properties

Name | Type
------------ | -------------
`workflow` | [Array&lt;StatusSchema&gt;](StatusSchema.md)
`id` | number
`name` | string
`color` | string
`taskCount` | number
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { ProjectDetailSchema } from ''

// TODO: Update the object below with actual values
const example = {
  "workflow": null,
  "id": null,
  "name": null,
  "color": null,
  "taskCount": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies ProjectDetailSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ProjectDetailSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


