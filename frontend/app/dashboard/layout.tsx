"use client";

import { Footer, Header, ProgressStepper } from "@/components";
import { Container } from "@mui/material";
import React from "react";
import { useStepper } from "@/app/context";

function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { currentStep, steps, navigateToStep } = useStepper();

  return (
    <>
      <Header />
      <Container maxWidth="xl" sx={{ pt: 12, pb: 12, flexGrow: 1 }}>
      <ProgressStepper
        activeStep={currentStep}
        steps={steps.map(step => step.label)}
        onStepClick={navigateToStep}
      />
      {children}
      </Container>
      <Footer />
    </>
  );
}

export default DashboardLayout;
