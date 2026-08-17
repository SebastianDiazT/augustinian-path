import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';

export interface SelectOption {
    value: string;
    label: string;
}

interface CustomSelectProps {
    id?: string;
    value: string;
    onChange: (value: string) => void;
    options: SelectOption[];
    placeholder?: string;
    disabled?: boolean;
}

export function CustomSelect({
    id,
    value,
    onChange,
    options,
    placeholder = 'Seleccionar...',
    disabled = false,
}: CustomSelectProps) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const selectedLabel = options.find((opt) => opt.value === value)?.label;

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [isOpen]);

    return (
        <div className='relative w-full text-sm' ref={dropdownRef}>
            <button
                id={id}
                type='button'
                onClick={() => !disabled && setIsOpen(!isOpen)}
                disabled={disabled}
                className={`flex w-full items-center justify-between rounded-xl border px-4 py-3.5 text-left transition-all 
                    ${
                        disabled
                            ? 'cursor-not-allowed border-border/50 bg-background/50 text-muted-foreground opacity-60'
                            : 'cursor-pointer border-border bg-background text-foreground hover:border-primary/50 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
                    }
                    ${isOpen ? 'border-primary ring-2 ring-primary/20' : ''}
                `}
            >
                <span
                    className={`block truncate ${!selectedLabel ? 'text-muted-foreground' : 'font-medium'}`}
                >
                    {selectedLabel || placeholder}
                </span>
                <ChevronDown
                    className={`ml-2 size-4 shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180 text-primary' : 'text-muted-foreground'}`}
                />
            </button>

            <div
                className={`absolute left-0 top-[calc(100%+8px)] z-50 w-full overflow-hidden rounded-xl border border-border bg-background shadow-2xl transition-all duration-200 ease-in-out
                    ${isOpen ? 'translate-y-0 opacity-100 visible' : '-translate-y-2 opacity-0 invisible'}
                `}
            >
                <div className='max-h-60 overflow-y-auto p-1 custom-scrollbar'>
                    {options.length === 0 ? (
                        <div className='px-4 py-3 text-sm text-muted-foreground text-center'>
                            No hay opciones disponibles
                        </div>
                    ) : (
                        options.map((option) => {
                            const isSelected = option.value === value;
                            return (
                                <button
                                    key={option.value}
                                    type='button'
                                    onClick={() => {
                                        onChange(option.value);
                                        setIsOpen(false);
                                    }}
                                    className={`relative flex w-full cursor-pointer items-center rounded-lg px-3 py-2.5 text-left text-sm outline-none transition-colors
                                        ${
                                            isSelected
                                                ? 'bg-primary/10 text-primary font-bold'
                                                : 'text-foreground hover:bg-muted focus:bg-muted'
                                        }
                                    `}
                                >
                                    <span className='block truncate pr-8'>{option.label}</span>
                                    {isSelected && (
                                        <Check className='absolute right-3 size-4 text-primary' />
                                    )}
                                </button>
                            );
                        })
                    )}
                </div>
            </div>
        </div>
    );
}
