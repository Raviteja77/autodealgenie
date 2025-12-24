import { z } from "zod";

/**
 * Zod schema for search form validation
 * Includes cross-field validations for budget and year ranges
 */
export const SearchFormSchema = z
  .object({
    // Vehicle criteria
    make: z.string().optional(),
    model: z.string().optional(),
    yearMin: z
      .number()
      .min(2000, "Year must be 2000 or later")
      .max(2025, "Year cannot exceed 2025"),
    yearMax: z
      .number()
      .min(2000, "Year must be 2000 or later")
      .max(2025, "Year cannot exceed 2025"),
    mileageMax: z
      .number()
      .min(0, "Mileage must be at least 0")
      .max(200000, "Mileage cannot exceed 200,000"),
    carType: z.string().optional(),
    bodyType: z.string().optional(),
    fuelType: z.string().optional(),
    transmission: z.string().optional(),
    drivetrain: z.string().optional(),
    mustHaveFeatures: z.array(z.string()).optional(),
    userPriorities: z.string().optional(),

    // Financing criteria
    paymentMethod: z.enum(["cash", "finance", "both"]),
    budgetMin: z
      .number()
      .min(5000, "Budget must be at least $5,000")
      .max(100000, "Budget cannot exceed $100,000"),
    budgetMax: z
      .number()
      .min(5000, "Budget must be at least $5,000")
      .max(100000, "Budget cannot exceed $100,000"),
    downPayment: z
      .number()
      .min(0, "Down payment cannot be negative")
      .optional(),
    loanTerm: z.number().optional(),
    creditScore: z.enum(["excellent", "good", "fair", "poor"]).optional(),
    monthlyPaymentMax: z
      .number()
      .min(0, "Monthly payment cannot be negative")
      .optional(),
    tradeInValue: z
      .number()
      .min(0, "Trade-in value cannot be negative")
      .optional(),
  })
  .refine((data) => data.budgetMin <= data.budgetMax, {
    message: "Maximum budget must be greater than or equal to minimum budget",
    path: ["budgetMax"],
  })
  .refine((data) => data.yearMin <= data.yearMax, {
    message: "Maximum year must be greater than or equal to minimum year",
    path: ["yearMax"],
  })
  .refine(
    (data) => {
      // Validate down payment doesn't exceed budget regardless of payment method
      if (data.downPayment !== undefined && data.downPayment > 0) {
        return data.downPayment <= data.budgetMax;
      }
      return true;
    },
    {
      message: "Down payment cannot exceed maximum budget",
      path: ["downPayment"],
    }
  );

export type SearchFormData = z.infer<typeof SearchFormSchema>;

/**
 * Validate individual field
 */
export function validateSearchField(
  field: keyof SearchFormData,
  value: unknown,
  allData: Partial<SearchFormData>
): { success: boolean; error?: string } {
  try {
    // For cross-field validations, we need to validate the entire object
    if (["budgetMax", "budgetMin", "yearMax", "yearMin"].includes(field)) {
      SearchFormSchema.parse({ ...allData, [field]: value });
    } else {
      // For simple fields, validate just the field
      const fieldSchema = SearchFormSchema.shape[field];
      if (fieldSchema) {
        fieldSchema.parse(value);
      }
    }
    return { success: true };
  } catch (error) {
    if (process.env.NODE_ENV === "development") {
      console.error(`Validation failed for ${field}:`, error);
    }

    if (error instanceof z.ZodError) {
      const fieldError = error.issues.find((issue) =>
        issue.path.includes(field)
      );
      return {
        success: false,
        error: fieldError?.message || "Invalid value",
      };
    }
    return { success: false, error: "Validation error" };
  }
}
