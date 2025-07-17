# Documentation Update Command: Update Implementation Documentation

## Documentation Analysis

1. Review current documentation status:
   - Check `specs/implementation_status.md` for overall project status
   - Review implemented phase document (`specs/phase{N}_implementation_plan.md`)
   - Review `specs/flutter_structurizr_implementation_spec.md` and `specs/flutter_structurizr_implementation_spec_updated.md`
   - Review `specs/testing_plan.md` to ensure it is current given recent test passes, failures, and changes
   - Examine `CLAUDE.md` and `README.md` for project-wide documentation
   - Check for and document any new lessons learned or best practices in CLAUDE.md

2. Analyze implementation and testing results:
   - Review what was implemented in the last phase
   - Review testing results and coverage
   - Identify new best practices discovered during implementation
   - Note any implementation challenges and solutions
   - Cross-reference updated documentation with recent implementation and test results to ensure accuracy

## Documentation Updates

1. Update phase implementation document:
   - Mark completed tasks with ✅ status
   - Update implementation percentages
   - Add detailed notes on implementation approach
   - Document any deviations from original plan with justification
   - Add new sections if needed (lessons learned, best practices)
   - Document specific implementation details for complex components
   - Include a summary of any new troubleshooting tips or workflow improvements discovered during the phase

2. Update implementation status document:
   - Update phase completion percentages
   - Add or update implementation status for components
   - Add notes on implementation approach and decisions
   - Document best practices discovered during implementation
   - Note any challenges overcome and solutions implemented

3. Update implementation specification documents:
   - Mark completed items with ✅ or strikethrough but preserve original requirements
   - Add notes on implementation details where appropriate
   - Add references to implemented files and classes
   - Update any implementation guidance based on experience

4. Update CLAUDE.md and README.md if necessary:
   - Add new best practices
   - Update project status
   - Add new implementation guidance
   - Document known issues or limitations
   - Update usage examples to include new functionality

5. Document new testing procedures:
   - Add details on test files created
   - Include test running instructions
   - Document test coverage
   - Explain testing approach for complex components

## Documentation Formatting and Structure

1. Maintain consistent documentation style:
   - Use clear headings and sections
   - Include code examples where helpful
   - Use status indicators (✅, ⚠️, ❌) consistently
   - Maintain proper Markdown formatting

2. Ensure documentation completeness:
   - Cover all implemented features
   - Include usage examples
   - Document API changes or additions
   - Include troubleshooting guidance for common issues

## Guidelines

- DO NOT CREATE new specification files
- UPDATE existing files in the `specs/` directory
- Maintain consistent documentation style
- Include practical examples where appropriate
- Cross-reference related documentation sections
- Document best practices and lessons learned
- Provide clear status updates on project progress
- Update numerical completion percentages
- Ensure documentation reflects actual implementation

Provide a summary of documentation updates after completion, including:
1. Files updated
2. Major changes to documentation
3. Updated completion percentages
4. New best practices documented
5. Status of the overall project after this phase