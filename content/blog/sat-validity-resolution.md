---
author: Dhaval Bothra
date: 2025-01-10 08:22:24+0530
doc: 2025-01-10 08:22:24+0530
title: "SAT, Validity and Resolution..."
topics:
- Logic
- Resolution
- SAT
---
In this blog, I will try to go over my understanding of the **resolution refutation** proof system and how it gets derived from few fundamental results. Let's quickly go over some fundamental result which relates satisfiablity with validity.
# Relation between SAT and Validity
**Proposition** Let $\phi$ be a formula of propositional logic. Then $\phi$ is satisfiable iff $\neg \phi$ is not valid.

**Proof:** First, assume that $\phi$ is satisfiable. By definition, there exists a valuation of $\phi$ in which $\phi$ evaluates to T; but that means that $\neg \phi$ evaluates to F for that same valuation. Thus, $\neg \phi$ cannot be valid.

Second, assume that $\neg \phi$ is not valid. Then there must be a valuation of $\neg \phi$ in which $\neg \phi$ evaluates to F. Thus, $\phi$ evaluates to T and is therefore satisfiable. (Note that the valuations of $\phi$ are exactly the valuations of $\neg \phi$.)

This result is extremely useful since it essentially says that we need to provide a decision method for only one of these concepts. For example, let’s say that we have a method \(P\) for deciding whether any \(\phi\) is valid. We obtain a decision method for satisfiability simply by asking \(P\) whether \(\neg \phi\) is valid. If it is, \(\phi\) is **not satisfiable**; otherwise, \(\phi\) is **satisfiable**. Similarly, we may transform any decision method for satisfiability into one for validity.

# Resolution Method

**Resolution** is a single, powerful rule used in propositional logic to check satisfiability. To be precise, it is used for proving **unsatisfiablity** of a set of clauses. Below is the resolution rule and a small example of its usage.  

## Resolution Rule
If you have two clauses:

- \(A \lor B\)  
- \(\neg A \lor C\)  

You can **resolve** them on \(A\) to produce a new clause:

\[
B \lor C
\]

This allows us to gradually simplify a set of clauses. If we can derive the empty clause \(\bot\), it shows the system is **unsatisfiable**.

### Example: Unsatisfiable System

Consider the set of clauses:

1. \(p \lor q\)  
2. \(\neg p \lor q\)  
3. \(p \lor \neg q\)  
4. \(\neg p \lor \neg q\)  

We can apply resolution step by step:



1. Resolve (1) \(p \lor q\) and (2) \(\neg p \lor q\) on \(p\):

\[
q \lor q = q
\]

2. Resolve \(q\) with (3) \(p \lor \neg q\) on \(q\):

\[
p
\]


3. Resolve \(q\) with (4) \(\neg p \lor \neg q\) on \(q\):

\[
\neg p
\]

4. Resolve \(p\) and \(\neg p\) to get the **empty clause**:

\[
\bot
\]

Since we derived \(\bot\), the system of clauses is **unsatisfiable**.


# Resolution Refutation 
So we can see that the **resolution method** can be used for showing **unsatisfiability** of a system. However, is it possible to use the **resolution method** as a **proof system** like **Natural Deduction**?

Say we want to prove \(\phi_1, \phi_2, \dots \models \psi\). This is **semantically equivalent** to checking the **validity** of the formula:

\[
(\phi_1 \land \phi_2 \land \dots) \to \psi
\]

From the **earlier proposition **, if a formula \(\phi\) is **valid**, then \(\neg \phi\) is **not satisfiable**.  
So, to check validity, we consider the **negation**:

\[
\neg \big((\phi_1 \land \phi_2 \land \dots) \to \psi\big)
\]

Recall that \(A \to B\) is equivalent to \(\neg A \lor B\). Applying this, we get:

\[
\neg \big( \neg (\phi_1 \land \phi_2 \land \dots) \lor \psi \big)
\]

Using **De Morgan's law** on the negation of a disjunction, we obtain:

\[
\neg \big( \neg (\phi_1 \land \phi_2 \land \dots) \big) \land \neg \psi
\]

Simplifying the double negation gives:

\[
(\phi_1 \land \phi_2 \land \dots) \land \neg \psi
\]

Thus, to prove \(\psi\) from \(\phi_1, \phi_2, \dots\), it suffices to check whether the set of clauses

\[
\{\phi_1, \phi_2, \dots, \neg \psi\}
\]

is **unsatisfiable** using the **resolution method**.


This, my friends, is exactly the **resolution refutation** proof system!

