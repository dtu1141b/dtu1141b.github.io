---
author: Dhaval Bothra
title: "Bernoulli Sampling in C++"
date: 2026-01-13T10:25:46+05:30
topics:
- RNG
- Number Theory
- C++ Implementation
---

> *How do you simulate randomness on a deterministic machine?*
> This post walks through a basic implementation of Bernoulli Sampling in C++.

---

# What is Bernoulli Sampling?

A **Bernoulli random variable** $X$ with parameter $p \in [0,1]$ satisfies:

$$
P(X = 1) = p, \qquad P(X = 0) = 1 - p
$$

This models a biased coin:

- Heads with probability $p$
- Tails with probability $1-p$

In C++ this is exactly what `std::bernoulli_distribution` does.  
Here I try to build it without using the standard library distributions.    



# Foundations: Uniform Random Numbers

Virtually all modern random number generation systems rely on a source of **uniformly distributed random numbers** on the interval [0,1).

Let $U$ be a random variable such that

$$
U \sim \mathcal{U}(0,1)
$$

This means $U$ has the cumulative distribution function (CDF):

$$
F_U(x) = P(U \le x) = 
\begin{cases} 
0 & \text{if } x < 0 \\
x & \text{if } 0 \le x \le 1 \\
1 & \text{if } x > 1 
\end{cases}
$$

Equivalently, for $x \in [0,1]$ we simply write:

$$
P(U \le x) = x
$$

Almost **every distribution** (continuous, discrete, or mixed) can be constructed by applying appropriate deterministic transformations to one or more independent $\mathcal{U}(0,1)$ random variables. This process is known [Inverse transform sampling](https://en.wikipedia.org/wiki/Inverse_transform_sampling).



# Building a Uniform RNG: Linear Congruential Generator

Almost all practical pseudorandom number generators start from a simple, fast, deterministic recurrence that produces numbers **that appear statistically random** and are **uniformly distributed** (i.e they have same frequency) in the desired interval.

One of the oldest, fastest, and still widely used methods is the **Linear Congruential Generator (LCG)**.

The recurrence is defined as:

$$
X_{n+1} = (a \cdot X_n + c) \bmod m
$$

where:
- $m$ is the **modulus** (usually a large power of 2 or a large prime),
- $a$ is the **multiplier**,
- $c$ is the **increment** (can be 0 → then it's a multiplicative congruential generator),
- $X_0$ is the **seed** (initial value, $0 \le X_0 < m$).

The generated integers $X_n$ lie in the range $\{0, 1, \dots, m-1\}$.

To obtain uniform random numbers in the continuous interval $[0,1)$, we normalize:

$$
U_n = \frac{X_n}{m}
$$

This gives $U_n \in [0,1)$ with (approximately) uniform distribution, **provided the parameters are chosen carefully**.

## Hull–Dobell Theorem: Conditions for Full Period

For an LCG to achieve its **maximum possible period** of $m$ (i.e., generate all possible values $0,1,\dots,m-1$ exactly once before repeating), the following conditions must hold and are sufficient([Hull & Dobell, 1962](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbmRTS2lOMzdZTTF2WWtMZXcxWHFpMkNNa2ZyQXxBQ3Jtc0tsSGQyX3pBdjkzblBTdVQ0VW13VE9GZm1kU2JaMm1xZldNRi1JS0ZDWTkxYW0yc2x3dnYtZzd2WElQaUJKNWlqUVpLZUE1YUNydGFaY2phWEJKa3pZNEdRNGp5RU85NDRkMV9LMWgwM3J4QkJ2WVAyNA&q=https%3A%2F%2Fdspace.library.uvic.ca%2Fbitstream%2Fhandle%2F1828%2F3142%2FRandom_Number_Generators.pdf%3Fsequence%3D3&v=kRCmR4qr-hQ)):

1. $c$ and $m$ are **relatively prime** → $\gcd(c, m) = 1$  
2. $a \equiv 1 \pmod{p}$ for every prime $p$ that divides $m$  
3. $a \equiv 1 \pmod{4}$ if $4$ divides $m$

**Popular practical choices** that satisfy the full-period conditions can be found over [here](https://en.wikipedia.org/wiki/Linear_congruential_generator#Parameters_in_common_use)
  
A badly chosen LCG can have a very short period, strong recognizable patterns, or poor statistical properties.  
But with parameters satisfying Hull–Dobell conditions and passing modern statistical test suites (TestU01, PractRand, etc.), LCGs can still serve as acceptable lightweight uniform generators, especially when speed is critical and cryptographic randomness is not required.

## Implementation

```cpp
class LCG {
    uint32_t state;
public:
    LCG(uint32_t seed) : state(seed) {}

    uint32_t next() {
        state = (1103515245u * state + 12345u);
        return state;
    }

    double uniform() {
        return (next() >> 1) / (double)(1u << 31);
    }
};
```

This is just a C++ implementation of LCG where the parameter values of glic(GCC) have been used, which produces floating-point numbers that behave approximately like $U_n \in [0,1)$.



# Generating a Bernoulli Random Variable from Uniform

Let $U \sim \mathcal{U}(0,1)$ be a uniform random variable on the interval $[0,1)$.

We define the Bernoulli random variable $X \in \{0,1\}$ as follows:

$$
X = 
\begin{cases} 
1 & \text{if } U < p \\
0 & \text{otherwise}
\end{cases}
$$

where $p \in [0,1]$ is the desired success probability.

## Proof that $X \sim \text{Bernoulli}(p)$

We verify the probability mass function directly:

$$
\begin{align*}
P(X = 1) &= P(U < p) \\
&= \int_0^p f_U(u)\, du \qquad \text{(since $U$ has density $f_U(u) = 1$ for $u \in [0,1)$)} \\
&= \int_0^p 1 \, du \\
&= p
\end{align*}
$$

and similarly,

$$
\begin{align*}
P(X = 0) &= P(U \ge p) \\
&= 1 - P(U < p) \\
&= 1 - p.
\end{align*}
$$

Thus, $X$ takes the value 1 with probability $p$ and the value 0 with probability $1-p$, which is precisely the definition of a **Bernoulli random variable** with parameter $p$:

$$
X \sim \text{Bernoulli}(p)
$$

This construction is extremely efficient as it uses only one comparison on the uniform random variable.



## Implementation

```cpp
class Bernoulli {
    double p;
    LCG &rng;

public:
    Bernoulli(double p, LCG &rng) : p(p), rng(rng) {}

    int sample() {
        double u = rng.uniform();
        return (u < p) ? 1 : 0;
    }
};
```

That’s it.


# Testing Correctness

```cpp
#include <iostream>
#include <cstdint>

int main() {
    LCG rng(123456);        
    Bernoulli B(0.3, rng);  

    int trials = 100000;
    int ones = 0;

    for (int i = 0; i < trials; i++) {
        ones += B.sample();
    }

    std::cout << "Estimated p = "
              << (double)ones / trials << std::endl;
}
```

Output:

```
Estimated p = 0.3015
```

As trials increase, the estimate converges to $p$ by the **Law of Large Numbers**.

