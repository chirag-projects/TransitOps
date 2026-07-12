import './Sidebar.css'

export type SidebarItem = {
  label: string
}

type SidebarProps = {
  items: SidebarItem[]
  activeItem: string
  onSelect: (label: string) => void
}

export function Sidebar({ items, activeItem, onSelect }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__mark">T</div>
        <div>
          <p className="sidebar__title">TransitOps</p>
          <p className="sidebar__subtitle">Operations console</p>
        </div>
      </div>

      <nav className="sidebar__nav" aria-label="Primary">
        {items.map((item) => {
          const isActive = item.label === activeItem

          return (
            <button
              key={item.label}
              type="button"
              className={`sidebar__link${isActive ? ' sidebar__link--active' : ''}`}
              onClick={() => onSelect(item.label)}
              aria-current={isActive ? 'page' : undefined}
            >
              <span>{item.label}</span>
              <span className="sidebar__dot" aria-hidden="true" />
            </button>
          )
        })}
      </nav>
    </aside>
  )
}