import { useDroppable } from "@dnd-kit/react";
import { CollisionPriority } from "@dnd-kit/abstract";

export default function Column({
  children,
  id,
  name,
  highlighted = false,
}: {
  children: React.ReactNode;
  id: string;
  name: string;
  // Set by the board while a card is being dragged over this column. The
  // droppable's own `isDropTarget` only fires when the pointer is over empty
  // column space, so on its own the column stops highlighting the moment the
  // pointer is over one of its cards. Combining the two keeps the whole column
  // lit for the entire hover.
  highlighted?: boolean;
}) {
  const { isDropTarget, ref } = useDroppable({
    id,
    type: "column",
    accept: "item",
    collisionPriority: CollisionPriority.Low,
  });
  const active = isDropTarget || highlighted;
  const style = active ? { background: "#00000030" } : undefined;

  return (
    <div
      key={name}
      className="flex w-56 flex-col gap-4"
      ref={ref}
      style={style}
      data-testid={`column-${id}`}
      data-active={active ? "true" : "false"}
    >
      <div className="flex justify-center">
        <h1>{name}</h1>
      </div>

      {children}
    </div>
  );
}
