## Summary

The goal of this command is to verify the repo is in a working state and fix issues if they exist.

## Goals

Run CI checks and fix issues until repo is in a good state and then add files to staging. All commands are run from repo root.
0. Make sure repo is up to date via running `pnpm i`
1. Check that the linter passes by running `pnpm lint`
2. Check that types and build pass by running `pnpm nx run-many --targets=build:types,build:dist,build:app,generate:docs,dev:run,typecheck`. 
   If one of the specific commands fail, save tokens via only running that command while debugging
3. Check that tests pass via running `pnpm nx run-many --target=test:coverage`
   Source the .env file first before running if it exists
4. Check package.json is sorted via running `pnpm run sort-package-json`
5. Check packages are linted via running `pnpm nx run-many --targets=lint:package,lint:deps`
6. Double check. If you made any fixes run preceeding checks again. For example, if you made fixes on step 3. run steps 1., 2., and 3. again to doublecheck there wasn't a regression on the earlier step.
7. Add files to staging with `git status` and `git add`. Make sure you don't add any git submodules in the `lib/*` folders though

Do NOT continue on to the next step until the command listed succeeds. You may sometimes have prompts in between or have to debug but always continue on unless I specifically give you permission to skip a check.
Print the list of tasks with a checkmark emoji next to every step that passed at the very end

## Protocol when something breaks

Take the following steps if CI breaks

### 1. Explain why it's broke

- Whenever a test is broken first give think very hard and a complete explanation of what broke. Cite source code and logs that support your thesis.
- If you don't have source code or logs to support your thesis, think hard and look in codebase for proof. 
- Add console logs if it will help you confirm your thesis or find out why it's broke
- If you don't know why it's broke or there just isn't enough context ask for help

### 2. Fix issue

- Propose your fix
- Fully explain why you are doing your fix and why you believe it will work
- If your fix does not work go back to Step 1

### 3. Consider if same bug exists elsewhere

- Think hard about whether the bug might exist elsewhere and how to best find it and fix it

### 4. Clean up

Always clean up added console.logs after fixing

## Tips

Generally most functions and types like `createTevmNode` are in a file named `createTevmNode.js` with a type called `TevmNode.ts` and tests `createTevmNode.spec.ts`. We generally have one item per file so the files are easy to find.

### pnpm i

If this fails you should just abort because something is very wrong unless the issue is simply syntax error like a missing comma.

### pnpm lint

This is using biome to lint the entire codebase

### pnpm nx-run-many --targets=build:types,typecheck

These commands from step 2 check typescript types and when they are broken it's likely for typescript error reasons. It's generally a good idea to fix the issue if it's obvious.
If the proof of why your typescript type isn't already in context or obvious it's best to look for the typescript type for confirmation before attempting to fix it. THis includes looking for it in node_modules. If it's a tevm package it's in this monorepo. 
If you fail more than a few times here we should look at documentation

### Run tests

To run the tests run the nx command for test:coverage. NEVER RUN normal test command as that command will time out. Run on individual packages in the same order the previous command ran the packages 1 by 1.

Run tests 1 package at a time to make them easier to debug

We use vite for all our tests.

- oftentimes snapshot tests will fail. Before updating snapshot tests we should clearly explain our thesis for why the snapshot changes are expected
- whenever a test fails follow the Protocol for when something breaks
- It often is a good idea to test assumptions via adding console logs to test that any assumptions of things that are working as expected are true

## Never commit

Only add to staging never actually make a commit

## Go ahead and fix errors

Don't be afraid to make fixes to things as the typescript types and tests will warn us if anything else breaks. No need to skip the fixes because they are considered dangerous.

## When fixes are made

When a step requires code changes to fix always do following steps after you are finished fixing that step.

1. Run `pnpm run lint` to make sure files are formatted
2. ask the the user if they want to add files to staging first
3. suggest a commit message but don't actually do the commit let the user do it themselves
