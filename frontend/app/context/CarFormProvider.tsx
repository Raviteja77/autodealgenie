"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { z } from "zod";

/**
 * Car type enum matching backend
 */
export const CarTypeEnum = z.enum([
  "sedan",
  "suv",
  "truck",
  "coupe",
  "hatchback",
  "convertible",
  "wagon",
  "van",
  "other",
]);

/**
 * Fuel type enum matching backend
 */
export const FuelTypeEnum = z.enum([
  "gasoline",
  "diesel",
  "electric",
  "hybrid",
  "plug_in_hybrid",
]);

/**
 * Transmission type enum matching backend
 */
export const TransmissionTypeEnum = z.enum(["automatic", "manual", "cvt"]);

/**
 * Zod schema for car search form validation
 */
export const CarSearchSchema = z
  .object({
    make: z.string().min(1, "Make is required").max(100).optional(),
    model: z.string().min(1, "Model is required").max(100).optional(),
    budget_min: z.number().min(0, "Budget must be positive").optional(),
    budget_max: z.number().min(0, "Budget must be positive").optional(),
    car_type: CarTypeEnum.optional(),
    year_min: z
      .number()
      .min(1900, "Year must be 1900 or later")
      .max(2100, "Year must be before 2100")
      .optional(),
    year_max: z
      .number()
      .min(1900, "Year must be 1900 or later")
      .max(2100, "Year must be before 2100")
      .optional(),
    mileage_max: z.number().min(0, "Mileage must be positive").optional(),
    fuel_type: FuelTypeEnum.optional(),
    transmission: TransmissionTypeEnum.optional(),
    user_priorities: z.string().max(500, "Priorities are too long").optional(),
  })
  .refine(
    (data) => {
      if (data.budget_min !== undefined && data.budget_max !== undefined) {
        return data.budget_max > data.budget_min;
      }
      return true;
    },
    {
      message: "Maximum budget must be greater than minimum budget",
      path: ["budget_max"],
    },
  )
  .refine(
    (data) => {
      if (data.year_min !== undefined && data.year_max !== undefined) {
        return data.year_max >= data.year_min;
      }
      return true;
    },
    {
      message: "Maximum year must be greater than or equal to minimum year",
      path: ["year_max"],
    },
  );

export type CarSearchFormData = z.infer<typeof CarSearchSchema>;

/**
 * Car search form state interface
 */
interface CarFormState {
  data: Partial<CarSearchFormData>;
  errors: Record<string, string>;
  isSearching: boolean;
  isValid: boolean;
}

/**
 * Car form context interface
 */
interface CarFormContextType {
  state: CarFormState;
  updateField: (field: keyof CarSearchFormData, value: string | number) => void;
  validateField: (field: keyof CarSearchFormData) => boolean;
  validateForm: () => boolean;
  resetForm: () => void;
  searchCars: (
    onSearch: (data: CarSearchFormData) => Promise<void>,
  ) => Promise<void>;
  setFormData: (data: Partial<CarSearchFormData>) => void;
  loadSavedSearch: (data: Partial<CarSearchFormData>) => void;
}

const CarFormContext = createContext<CarFormContextType | undefined>(undefined);

/**
 * Initial car form state
 */
const initialState: CarFormState = {
  data: {},
  errors: {},
  isSearching: false,
  isValid: false,
};

/**
 * CarFormProvider component for managing car search form state
 * Provides car search form state management, validation using Zod, and search handling
 */
export function CarFormProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<CarFormState>(initialState);

  /**
   * Update a single field in the car search form
   */
  const updateField = useCallback(
    (field: keyof CarSearchFormData, value: string | number) => {
      setState((prev) => ({
        ...prev,
        data: { ...prev.data, [field]: value },
        errors: { ...prev.errors, [field]: "" }, // Clear error on update
      }));
    },
    [],
  );

  /**
   * Validate a single field using Zod
   */
  const validateField = useCallback(
    (field: keyof CarSearchFormData): boolean => {
      try {
        const fieldSchema = CarSearchSchema.shape[field];
        if (fieldSchema) {
          fieldSchema.parse(state.data[field]);
          setState((prev) => ({
            ...prev,
            errors: { ...prev.errors, [field]: "" },
          }));
          return true;
        }
        return true;
      } catch (error) {
        if (error instanceof z.ZodError) {
          const zodError = error as z.ZodError<CarSearchFormData>;
          setState((prev) => ({
            ...prev,
            errors: {
              ...prev.errors,
              [field]: zodError.issues[0]?.message || "Invalid value",
            },
          }));
        }
        return false;
      }
    },
    [state.data],
  );

  /**
   * Validate the entire car search form using Zod
   */
  const validateForm = useCallback((): boolean => {
    try {
      CarSearchSchema.parse(state.data);
      setState((prev) => ({ ...prev, errors: {}, isValid: true }));
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const zodError = error as z.ZodError<CarSearchFormData>;
        const errors: Record<string, string> = {};
        zodError.issues.forEach((err: z.ZodIssue) => {
          if (err.path[0]) {
            errors[err.path[0].toString()] = err.message;
          }
        });
        setState((prev) => ({ ...prev, errors, isValid: false }));
      }
      return false;
    }
  }, [state.data]);

  /**
   * Reset the car search form to initial state
   */
  const resetForm = useCallback(() => {
    setState(initialState);
  }, []);

  /**
   * Execute car search with validation
   */
  const searchCars = useCallback(
    async (onSearch: (data: CarSearchFormData) => Promise<void>) => {
      if (!validateForm()) {
        return;
      }

      setState((prev) => ({ ...prev, isSearching: true }));

      try {
        await onSearch(state.data as CarSearchFormData);
        // Don't reset form after search - keep the criteria for refinement
      } catch (error) {
        console.error("Car search error:", error);
        throw error;
      } finally {
        setState((prev) => ({ ...prev, isSearching: false }));
      }
    },
    [state.data, validateForm],
  );

  /**
   * Set multiple form fields at once
   */
  const setFormData = useCallback((data: Partial<CarSearchFormData>) => {
    setState((prev) => ({
      ...prev,
      data: { ...prev.data, ...data },
    }));
  }, []);

  /**
   * Load a saved search into the form
   */
  const loadSavedSearch = useCallback((data: Partial<CarSearchFormData>) => {
    setState((prev) => ({
      ...prev,
      data: { ...data },
      errors: {},
      isValid: false,
    }));
  }, []);

  return (
    <CarFormContext.Provider
      value={{
        state,
        updateField,
        validateField,
        validateForm,
        resetForm,
        searchCars,
        setFormData,
        loadSavedSearch,
      }}
    >
      {children}
    </CarFormContext.Provider>
  );
}

/**
 * Hook to use the car form context
 * Must be used within a CarFormProvider
 */
export function useCarForm() {
  const context = useContext(CarFormContext);
  if (context === undefined) {
    throw new Error("useCarForm must be used within a CarFormProvider");
  }
  return context;
}

/**
 * Type exports for external use
 */
export type { CarFormState, CarFormContextType };
