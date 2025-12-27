/**
 * Type definitions for Vehicle Info Display molecules
 */

export interface VehicleDetailsProps {
  mileage: number;
  fuelType?: string;
  condition?: string;
  location?: string;
  compact?: boolean;
}

export interface VehicleTitleProps {
  make: string;
  model: string;
  year: number;
  variant?: 'h4' | 'h5' | 'h6';
}

export interface VehicleImageProps {
  image?: string;
  make: string;
  model: string;
  year: number;
  badges?: React.ReactNode[];
  actions?: React.ReactNode[];
}
