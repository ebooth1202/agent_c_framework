echo.
echo Installing required dependencies...
call npm install @radix-ui/react-avatar @radix-ui/react-dialog @radix-ui/react-hover-card @radix-ui/react-checkbox @radix-ui/react-select @radix-ui/react-slot @radix-ui/react-toast @radix-ui/react-tooltip @radix-ui/react-tabs @radix-ui/react-progress @radix-ui/react-label @radix-ui/react-switch @radix-ui/react-separator @radix-ui/react-collapsible @radix-ui/react-scroll-area @radix-ui/react-alert-dialog @radix-ui/react-slider
echo.

echo Installing additional required packages...
call npm install @radix-ui/react-icons @radix-ui/themes class-variance-authority clsx tailwind-merge lucide-react

echo.
echo Installing Basic UI components...

call npx shadcn@latest add button card input
echo.

echo Installing Form components...
call npx shadcn@latest add avatar badge checkbox label select slider switch textarea


echo.
echo Installing Layout components...
call npx shadcn@latest add collapsible scroll-area separator tabs


echo.
echo Installing Overlay components...
call npx shadcn@latest add alert alert-dialog dialog hover-card toast tooltip


echo.
echo Installing Feedback components...
call npx shadcn@latest add progress

echo.
echo Installation complete! Please restart your development server.