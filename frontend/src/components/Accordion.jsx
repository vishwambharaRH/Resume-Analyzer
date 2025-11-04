import React, { createContext, useContext, useState } from 'react';
import { ChevronDown } from 'lucide-react';

const AccordionContext = createContext(undefined);

const useAccordion = () => {
  const context = useContext(AccordionContext);
  if (!context) {
    throw new Error('Accordion components must be used within an Accordion');
  }
  return context;
};

export const Accordion = ({ children, defaultOpen, allowMultiple = false, className = '' }) => {
  const [activeItems, setActiveItems] = useState(defaultOpen ? [defaultOpen] : []);

  const toggleItem = (id) => {
    setActiveItems((prev) => {
      if (allowMultiple) {
        return prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id];
      } else {
        return prev.includes(id) ? [] : [id];
      }
    });
  };

  const isItemActive = (id) => activeItems.includes(id);

  return (
    <AccordionContext.Provider value={{ activeItems, toggleItem, isItemActive }}>
      <div className={`space-y-2 ${className}`}>{children}</div>
    </AccordionContext.Provider>
  );
};

export const AccordionItem = ({ id, children, className = '' }) => {
  return (
    <div className={`overflow-hidden border-b border-gray-200 ${className}`}>
      {children}
    </div>
  );
};

export const AccordionHeader = ({ itemId, children, className = '' }) => {
  const { toggleItem, isItemActive } = useAccordion();
  const isActive = isItemActive(itemId);

  return (
    <button
      onClick={() => toggleItem(itemId)}
      className={`w-full px-6 py-4 text-left focus:outline-none transition-colors duration-200 flex items-center justify-between cursor-pointer hover:bg-gray-50 ${className}`}
    >
      <div className="flex-1">{children}</div>
      <ChevronDown
        className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
          isActive ? 'rotate-180' : ''
        }`}
      />
    </button>
  );
};

export const AccordionContent = ({ itemId, children, className = '' }) => {
  const { isItemActive } = useAccordion();
  const isActive = isItemActive(itemId);

  return (
    <div
      className={`overflow-hidden transition-all duration-300 ease-in-out ${
        isActive ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
      } ${className}`}
    >
      <div className="px-6 py-4">{children}</div>
    </div>
  );
};