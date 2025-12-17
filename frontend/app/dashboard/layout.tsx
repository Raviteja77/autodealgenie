"use client";

import { Footer, Header, ProgressStepper } from "@/components";
import { Container } from "@mui/material";
import React from "react";

function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <Container maxWidth="xl" sx={{ pt: 12, pb: 12, flexGrow: 1 }}>
      <ProgressStepper
        activeStep={0}
        steps={["Search", "Results", "Negotiate", "Evaluate", "Finalize"]}
      />
      {children}
      </Container>
      <Footer />
    </>
  );
}

export default DashboardLayout;
