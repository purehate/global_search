/** @odoo-module */

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Spotlight-style global search component.
 *
 * Renders a small search icon in the systray. Opens a full-screen
 * overlay dialog on click or Ctrl+K / Cmd+K. Searches across
 * configured models via JSON-RPC and supports keyboard navigation.
 */
export class GlobalSearchSystray extends Component {
    static template = "global_search.GlobalSearchSystray";

    setup() {
        this.rpc = useService("rpc");
        this.actionService = useService("action");

        this.state = useState({
            isOpen: false,
            query: "",
            results: [],
            isLoading: false,
            selectedIndex: -1,
        });

        this.inputRef = useRef("searchInput");
        this._searchTimeout = null;

        // Global keyboard shortcut: Ctrl+K / Cmd+K
        this._onGlobalKeyDown = this._onGlobalKeyDown.bind(this);
        onMounted(() => {
            document.addEventListener("keydown", this._onGlobalKeyDown, true);
        });
        onWillUnmount(() => {
            document.removeEventListener("keydown", this._onGlobalKeyDown, true);
            if (this._searchTimeout) {
                clearTimeout(this._searchTimeout);
            }
        });
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    /**
     * Returns the result groups with a flat index on each record,
     * used for keyboard navigation highlighting.
     */
    get flatResults() {
        let idx = 0;
        const groups = [];
        for (const group of this.state.results) {
            const records = [];
            for (const record of group.records) {
                records.push({
                    id: record.id,
                    name: record.name,
                    flatIndex: idx++,
                });
            }
            groups.push({
                model: group.model,
                model_name: group.model_name,
                icon: group.icon,
                records,
            });
        }
        return groups;
    }

    /** Total number of selectable result items. */
    get totalResults() {
        let total = 0;
        for (const group of this.state.results) {
            total += group.records.length;
        }
        return total;
    }

    /** Whether to display the "no results" message. */
    get showNoResults() {
        return (
            this.state.query.length >= 2 &&
            !this.state.results.length &&
            !this.state.isLoading
        );
    }

    /** Whether to display the initial hint text. */
    get showHint() {
        return this.state.query.length < 2 && !this.state.results.length;
    }

    // -------------------------------------------------------------------------
    // Actions
    // -------------------------------------------------------------------------

    /** Open the search overlay and focus the input. */
    open() {
        this.state.isOpen = true;
        this.state.query = "";
        this.state.results = [];
        this.state.selectedIndex = -1;
        // Wait for DOM update before focusing
        requestAnimationFrame(() => {
            if (this.inputRef.el) {
                this.inputRef.el.focus();
            }
        });
    }

    /** Close the overlay and reset state. */
    close() {
        this.state.isOpen = false;
        this.state.query = "";
        this.state.results = [];
        this.state.selectedIndex = -1;
        if (this._searchTimeout) {
            clearTimeout(this._searchTimeout);
        }
    }

    /** Toggle the overlay open/closed. */
    toggleOpen() {
        if (this.state.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Navigate to a record's form view.
     * @param {string} model - Technical model name.
     * @param {number} resId - Record ID.
     */
    openRecord(model, resId) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            res_id: resId,
            views: [[false, "form"]],
            target: "current",
        });
        this.close();
    }

    // -------------------------------------------------------------------------
    // Search
    // -------------------------------------------------------------------------

    /** Perform the debounced RPC search. */
    async _doSearch() {
        try {
            const results = await this.rpc("/global_search/search", {
                query: this.state.query,
            });
            this.state.results = results;
        } catch (err) {
            this.state.results = [];
        }
        this.state.isLoading = false;
    }

    // -------------------------------------------------------------------------
    // Event handlers
    // -------------------------------------------------------------------------

    /** Global keydown: Ctrl+K / Cmd+K to toggle overlay. */
    _onGlobalKeyDown(ev) {
        if ((ev.metaKey || ev.ctrlKey) && ev.key === "k") {
            ev.preventDefault();
            ev.stopPropagation();
            this.toggleOpen();
        }
    }

    /** Systray icon click. */
    onIconClick() {
        this.toggleOpen();
    }

    /** Backdrop click — close only if clicking the backdrop itself. */
    onBackdropClick(ev) {
        if (ev.target === ev.currentTarget) {
            this.close();
        }
    }

    /** Search input handler with 300ms debounce. */
    onInput(ev) {
        this.state.query = ev.target.value;
        this.state.selectedIndex = -1;
        if (this._searchTimeout) {
            clearTimeout(this._searchTimeout);
        }
        if (this.state.query.length < 2) {
            this.state.results = [];
            this.state.isLoading = false;
            return;
        }
        this.state.isLoading = true;
        this._searchTimeout = setTimeout(() => this._doSearch(), 300);
    }

    /** Keyboard navigation inside the search input. */
    onKeydown(ev) {
        const total = this.totalResults;
        if (ev.key === "Escape") {
            ev.preventDefault();
            this.close();
        } else if (ev.key === "ArrowDown") {
            ev.preventDefault();
            if (this.state.selectedIndex < total - 1) {
                this.state.selectedIndex++;
            }
            this._scrollSelectedIntoView();
        } else if (ev.key === "ArrowUp") {
            ev.preventDefault();
            if (this.state.selectedIndex > 0) {
                this.state.selectedIndex--;
            }
            this._scrollSelectedIntoView();
        } else if (ev.key === "Enter" && this.state.selectedIndex >= 0) {
            ev.preventDefault();
            this._openSelectedResult();
        }
    }

    /** Click on a result row. */
    onResultClick(ev) {
        const el = ev.currentTarget;
        const model = el.dataset.resModel;
        const resId = parseInt(el.dataset.resId, 10);
        this.openRecord(model, resId);
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /** Open the currently keyboard-selected result. */
    _openSelectedResult() {
        let idx = 0;
        for (const group of this.state.results) {
            for (const record of group.records) {
                if (idx === this.state.selectedIndex) {
                    this.openRecord(group.model, record.id);
                    return;
                }
                idx++;
            }
        }
    }

    /** Scroll the highlighted result into view after arrow-key navigation. */
    _scrollSelectedIntoView() {
        requestAnimationFrame(() => {
            const el = document.querySelector(".o_gs_result.selected");
            if (el) {
                el.scrollIntoView({ block: "nearest" });
            }
        });
    }
}

export const globalSearchSystray = {
    Component: GlobalSearchSystray,
};

registry
    .category("systray")
    .add("global_search.GlobalSearchSystray", globalSearchSystray, {
        sequence: 100,
    });
