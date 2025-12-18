"use client";

import { Footer, Header } from "@/components";
import { Box, Container } from "@mui/material";
import React from "react";

function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <Box>
      <Header noButton={true} />
      <Container maxWidth="sm" sx={{ mt: 16, mb: 6 }}>
        {children}
      </Container>
      <Footer />
    </Box>
  );
}

export default AuthLayout;
