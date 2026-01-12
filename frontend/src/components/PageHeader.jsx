import React from 'react'
import { Link } from 'react-router-dom'

/**
 * Reusable Page Header Component
 * Provides consistent styling across all pages
 * 
 * @param {string} title - Main page title
 * @param {string} subtitle - Optional subtitle/description
 * @param {React.ReactNode} actions - Optional action buttons/elements (rendered on the right)
 * @param {string} backLink - Optional back link URL
 * @param {string} backLabel - Optional back link label (default: "Back")
 * @param {string} variant - Header variant: 'default' | 'card' | 'simple'
 * @param {React.ReactNode} icon - Optional icon element
 * @param {string} titleColor - Optional title color class (default: 'text-gray-900')
 */
const PageHeader = ({
  title,
  subtitle,
  actions,
  backLink,
  backLabel = 'Back',
  variant = 'default',
  icon,
  titleColor = 'text-gray-900'
}) => {
  // Default variant: Simple flex layout (most common)
  if (variant === 'default') {
    return (
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            {icon && <div className="flex-shrink-0">{icon}</div>}
            <div>
              <h1 className={`text-3xl font-bold ${titleColor}`}>{title}</h1>
              {subtitle && (
                <p className="text-gray-600 mt-2">{subtitle}</p>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4 ml-4">
          {backLink && (
            <Link
              to={backLink}
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
            >
              ← {backLabel}
            </Link>
          )}
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      </div>
    )
  }

  // Card variant: White card with shadow (like Dashboard)
  if (variant === 'card') {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            {icon && <div className="flex-shrink-0">{icon}</div>}
            <div>
              <h1 className={`text-3xl font-bold ${titleColor} mb-1`}>{title}</h1>
              {subtitle && (
                <p className="text-gray-600 text-sm">{subtitle}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-4">
            {backLink && (
              <Link
                to={backLink}
                className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
              >
                ← {backLabel}
              </Link>
            )}
            {actions && <div className="flex items-center gap-2">{actions}</div>}
          </div>
        </div>
      </div>
    )
  }

  // Simple variant: Minimal styling (for pages with tabs or other complex layouts)
  if (variant === 'simple') {
    return (
      <div>
        <div className="flex items-center gap-3">
          {icon && <div className="flex-shrink-0">{icon}</div>}
          <div>
            <h1 className={`text-3xl font-bold ${titleColor}`}>{title}</h1>
            {subtitle && (
              <p className="text-gray-600 mt-2">{subtitle}</p>
            )}
          </div>
        </div>
        {actions && (
          <div className="mt-4 flex items-center gap-2">{actions}</div>
        )}
      </div>
    )
  }

  return null
}

export default PageHeader
