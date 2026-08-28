interface LogoProps {
  className?: string;
}

// Brand-colored payment marks. Unlike the monochrome lucide icons they sit
// alongside, these keep their real brand colors regardless of selection
// state — className only controls sizing (w-*/h-*), never fill.

export function VisaLogo({ className }: LogoProps) {
  return (
    <svg viewBox="0 0 48 32" className={className} role="img" aria-label="Visa">
      <rect x="0.5" y="0.5" width="47" height="31" rx="5.5" fill="#fff" stroke="#e2e2e2" />
      <text
        x="24"
        y="21.5"
        textAnchor="middle"
        fontFamily="Arial, Helvetica, sans-serif"
        fontSize="14"
        fontWeight="800"
        fontStyle="italic"
        letterSpacing="-0.5"
        fill="#1A1F71"
      >
        VISA
      </text>
    </svg>
  );
}

export function MastercardLogo({ className }: LogoProps) {
  return (
    <svg viewBox="0 0 48 32" className={className} role="img" aria-label="Mastercard">
      <rect x="0.5" y="0.5" width="47" height="31" rx="5.5" fill="#fff" stroke="#e2e2e2" />
      <circle cx="20" cy="16" r="9" fill="#EB001B" />
      <circle cx="28" cy="16" r="9" fill="#F79E1B" />
      <path
        d="M24 9.4a9 9 0 0 1 0 13.2 9 9 0 0 1 0-13.2Z"
        fill="#FF5F00"
      />
    </svg>
  );
}

export function CardBrandsLogo({ className }: LogoProps) {
  return (
    <span className={`inline-flex items-center gap-1 ${className ?? ""}`}>
      <VisaLogo className="h-full w-auto" />
      <MastercardLogo className="h-full w-auto" />
    </span>
  );
}

export function MpesaLogo({ className }: LogoProps) {
  return (
    <svg viewBox="0 0 48 32" className={className} role="img" aria-label="M-Pesa">
      <rect width="48" height="32" rx="6" fill="#4CAF50" />
      <text
        x="24"
        y="20.5"
        textAnchor="middle"
        fontFamily="Arial, Helvetica, sans-serif"
        fontSize="11"
        fontWeight="800"
        letterSpacing="-0.3"
        fill="#fff"
      >
        M-PESA
      </text>
    </svg>
  );
}
