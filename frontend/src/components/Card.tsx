import type { ReactNode } from "react";
import styles from "./Card.module.css";

interface CardProps {
  /** Optional heading shown at the top of the card. */
  title?: ReactNode;
  /** Optional content aligned to the right of the heading. */
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}

/** Surface container used for every block of the page. */
export function Card({ title, actions, children, className }: CardProps) {
  return (
    <section className={[styles.card, className].filter(Boolean).join(" ")}>
      {(title || actions) && (
        <header className={styles.header}>
          {title && <h2 className={styles.title}>{title}</h2>}
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}
