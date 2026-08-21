import { useAppStore } from "@/stores/app-store";

export default function ProjectSelector() {
  const setProject = useAppStore((state) => state.setKanbanSelectedProject);
  const selectedProject = useAppStore((state) => state.kanbanSelectedProject);
  const projects = useAppStore((state) => state.projects);

  return (
    <div className="dropdown">
      <div tabIndex={0} role="button" className="btn m-1">
        {selectedProject?.name ?? "Select project"}
        <svg
          width="12px"
          height="12px"
          className="inline-block h-2 w-2 fill-current opacity-60"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 2048 2048"
        >
          <path d="M1799 349l242 241-1017 1017L7 590l242-241 775 775 775-775z"></path>
        </svg>
      </div>
      <ul
        tabIndex={-1}
        className="dropdown-content bg-base-300 rounded-box z-1 w-52 p-2 shadow-2xl"
      >
        {projects.map((project) => (
          <li key={project.id}>
            <button
              type="button"
              className={
                project.id === selectedProject?.id ? "menu-active" : undefined
              }
              onClick={() =>
                selectedProject?.id === project.id
                  ? setProject(null)
                  : setProject(project)
              }
            >
              <span className="border-base-content/20 bg-primary inline-block size-4 rounded-full border" />
              {project.name}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
