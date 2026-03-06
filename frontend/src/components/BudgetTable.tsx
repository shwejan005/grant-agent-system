"use client";

import { motion } from "framer-motion";
import { Budget, BudgetCategory } from "@/lib/types";
import { Receipt } from "lucide-react";

interface BudgetTableProps {
    budget: Budget;
}

export default function BudgetTable({ budget }: BudgetTableProps) {
    const budgetTable: BudgetCategory[] = budget.budget_table || [];

    return (
        <div className="bg-white/50 backdrop-blur-md rounded-3xl border border-white shadow-xl shadow-foreground/5 overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-white/50 bg-white/30">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-white border border-border flex items-center justify-center shadow-sm">
                        <Receipt className="w-5 h-5 text-foreground" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-foreground">Budget Breakdown</h3>
                        <p className="text-[11px] font-medium text-muted uppercase tracking-widest mt-0.5">Estimated Limits</p>
                    </div>
                </div>
                {budget.total_budget && (
                    <div className="text-right">
                        <span className="text-[10px] uppercase font-bold text-muted block mb-1">Total Requested</span>
                        <span className="text-xl font-bold bg-foreground text-white px-3 py-1 rounded-xl tracking-tight">
                            ₹{budget.total_budget}
                        </span>
                    </div>
                )}
            </div>

            <div className="p-6 overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr>
                            <th className="pb-4 text-[10px] font-bold text-muted uppercase tracking-widest border-b border-border/40">Category</th>
                            <th className="pb-4 text-[10px] font-bold text-muted uppercase tracking-widest border-b border-border/40">Itemized Justification</th>
                            <th className="pb-4 text-[10px] font-bold text-muted uppercase tracking-widest border-b border-border/40 text-right">Amount</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border/30">
                        {budgetTable.map((category, catIdx) => (
                            <motion.tr
                                key={catIdx}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: catIdx * 0.1 }}
                                className="group hover:bg-white/40 transition-colors"
                            >
                                <td className="py-4 pr-4 font-bold text-xs text-foreground align-top whitespace-nowrap">
                                    {category.category}
                                </td>
                                <td className="py-4 px-4 align-top">
                                    <ul className="space-y-2">
                                        {category.items?.map((item, i) => (
                                            <li key={i} className="text-[13px] font-medium text-foreground/80 leading-snug">
                                                <span className="text-foreground">{item.item}</span>
                                                {item.justification && (
                                                    <span className="text-muted block mt-0.5 text-xs font-normal">
                                                        ↳ {item.justification}
                                                    </span>
                                                )}
                                            </li>
                                        )) || <li className="text-[13px] text-muted">—</li>}
                                    </ul>
                                </td>
                                <td className="py-4 pl-4 text-right font-bold text-sm text-foreground align-top">
                                    ₹{category.subtotal}
                                </td>
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {budget.cost_justification && (
                <div className="px-6 py-5 bg-surface-hover/50 border-t border-white/50">
                    <p className="text-xs text-foreground/70 font-medium leading-relaxed">
                        <span className="font-bold text-foreground">Global Justification: </span>
                        {budget.cost_justification}
                    </p>
                </div>
            )}
        </div>
    );
}
