# TODO: Add JavaScript Validations and Real-Time Alerts for Client Data Forms

## Tasks
- [ ] Add validation functions for RUT, phone, email, name in recepcion/templates/recepcion/index.html
- [ ] Implement real-time alerts (error messages below fields on input/blur)
- [ ] Add CSS styling for error states
- [ ] Prevent form submission if validations fail
- [ ] Test validations with sample data
- [ ] Optionally add to editar_cliente.html if needed

## Notes
- RUT: Chilean format with checksum validation
- Phone: 9 digits starting with 9
- Email: Standard regex
- Name: Not empty, min 3 characters
- Use Bootstrap alert classes for styling
