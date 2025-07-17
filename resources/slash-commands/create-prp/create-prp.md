YOU MUST READ THESE FILES AND FOLLOW THE INSTRUCTIONS IN THEM.
Start by reading the concept_library/cc_PRP_flow/README.md to understand what a PRP
Then read concept_library/cc_PRP_flow/PRPs/base_template_v1 to understand the structure of a PRP.

Think hard about the concept

Help the user create a comprehensive Product Requirement Prompt (PRP) for: $ARGUMENTS

## Instructions for PRP Creation

Research and develop a complete PRP based on the feature/product description above. Follow these guidelines:

## Research Process

Begin with thorough research to gather all necessary context:

1. **Documentation Review**

   - Check for relevant documentation in the `ai_docs/` directory
   - Identify any documentation gaps that need to be addressed
   - Ask the user if additional documentation should be referenced

2. **WEB RESEARCH**

   - Use web search to gather additional context
   - Research the concept of the feature/product
   - Look into library documentation
   - Look into example implementations on StackOverflow
   - Look into example implementations on GitHub
   - etc...
   - Ask the user if additional web search should be referenced

3. **Template Analysis**

   - Use `concept_library/cc_PRP_flow/PRPs/base_template_v1` as the structural reference
   - Ensure understanding of the template requirements before proceeding
   - Review past templates in the PRPs/ directory for inspiration if there are any

4. **Codebase Exploration**

   - Identify relevant files and directories that provide implementation context
   - Ask the user about specific areas of the codebase to focus on
   - Look for patterns that should be followed in the implementation

5. **Implementation Requirements**
   - Confirm implementation details with the user
   - Ask about specific patterns or existing features to mirror
   - Inquire about external dependencies or libraries to consider

## PRP Development

Create a PRP following the template in `concept_library/cc_PRP_flow/PRPs/base_template_v1`, ensuring it includes the same structure as the template.

## Context Prioritization

A successful PRP must include comprehensive context through specific references to:

- Files in the codebase
- Web search results and URL's
- Documentation
- External resources
- Example implementations
- Validation criteria

## User Interaction

After completing initial research, present findings to the user and confirm:

- The scope of the PRP
- Patterns to follow
- Implementation approach
- Validation criteria

If the user answers with continue, you are on the right path, continue with the PRP creation without user input.

Remember: A PRP is PRD + curated codebase intelligence + agent/runbook—the minimum viable packet an AI needs to ship production-ready code on the first pass.
