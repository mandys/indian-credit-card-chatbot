import streamlit as st
from typing import Dict, List, Optional, Any
from .qa_engine import RichDataCreditCardBot
import json

class CreditCardWizard:
    """
    A wizard-based interface for credit card queries that provides guided flow
    for structured queries and falls back to free-form text for complex cases.
    """
    
    def __init__(self, data_files: List[str]):
        # Initialize the existing QA engine for fallback
        self.qa_engine = RichDataCreditCardBot(data_files)
        
        # Initialize session state keys
        self._init_session_state()
        
        # Define wizard steps and options
        self.cards = {
            'icici_epm': {
                'name': 'ICICI Emeralde Private Metal',
                'full_name': 'ICICI Bank Emeralde Private Metal Credit Card',
                'emoji': '🏦',
                'color': '#FF6B35'
            },
            'axis_atlas': {
                'name': 'Axis Bank Atlas',
                'full_name': 'Axis Bank Atlas Credit Card', 
                'emoji': '🏦',
                'color': '#1E88E5'
            }
        }
        
        self.query_categories = {
            'rewards': {
                'name': '💰 Reward Rates & Calculations',
                'description': 'Points, miles, cashback rates and calculations',
                'subcategories': {
                    'general_rates': 'General earning rates',
                    'category_rates': 'Category-specific rates', 
                    'comparison': 'Compare rewards between cards',
                    'calculation': 'Calculate rewards for specific spend'
                }
            },
            'travel': {
                'name': '✈️ Travel & Airport Benefits', 
                'description': 'Lounge access, travel insurance, airport benefits',
                'subcategories': {
                    'lounge_access': 'Airport lounge access',
                    'travel_insurance': 'Travel insurance coverage',
                    'airport_benefits': 'Airport meet & greet, transfers',
                    'airline_benefits': 'Airline partnerships and benefits'
                }
            },
            'fees': {
                'name': '💳 Fees & Charges',
                'description': 'Annual fees, surcharges, transaction fees',
                'subcategories': {
                    'annual_fee': 'Annual fee and waiver conditions',
                    'surcharges': 'Category surcharges (fuel, utilities, etc.)',
                    'transaction_fees': 'Foreign transaction, cash advance fees',
                    'other_fees': 'Late payment, overlimit, replacement fees'
                }
            },
            'spending': {
                'name': '🎯 Spending Categories',
                'description': 'Rewards and fees for specific spending categories',
                'subcategories': {
                    'hotels_travel': '🏨 Hotels & Travel',
                    'utilities': '⚡ Utilities',
                    'rent': '🏠 Rent',
                    'fuel': '⛽ Fuel', 
                    'education': '🎓 Education',
                    'government': '🏛️ Government/Tax',
                    'gold_jewellery': '💍 Gold/Jewellery',
                    'insurance': '🛡️ Insurance',
                    'gaming': '🎮 Gaming',
                    'wallet': '📱 Wallet/UPI'
                }
            },
            'general': {
                'name': '📋 General Information',
                'description': 'Eligibility, welcome benefits, terms & conditions',
                'subcategories': {
                    'welcome_benefits': 'Welcome and joining benefits',
                    'eligibility': 'Eligibility criteria',
                    'milestones': 'Milestone benefits',
                    'insurance_coverage': 'Insurance coverage details'
                }
            },
            'other': {
                'name': '💬 Ask Anything Else',
                'description': 'Free-form questions using our smart AI assistant',
                'subcategories': {}
            }
        }
    
    def _init_session_state(self):
        """Initialize session state variables for the wizard"""
        if 'wizard_step' not in st.session_state:
            st.session_state.wizard_step = 'card_selection'
        if 'selected_cards' not in st.session_state:
            st.session_state.selected_cards = []
        if 'selected_category' not in st.session_state:
            st.session_state.selected_category = None
        if 'selected_subcategory' not in st.session_state:
            st.session_state.selected_subcategory = None
        if 'wizard_complete' not in st.session_state:
            st.session_state.wizard_complete = False
    
    def reset_wizard(self):
        """Reset wizard to initial state"""
        st.session_state.wizard_step = 'card_selection'
        st.session_state.selected_cards = []
        st.session_state.selected_category = None
        st.session_state.selected_subcategory = None
        st.session_state.wizard_complete = False
    
    def render_step_indicator(self):
        """Render a progress indicator for wizard steps"""
        steps = ['Card Selection', 'Query Category', 'Specific Details']
        current_step_idx = 0
        
        if st.session_state.wizard_step == 'card_selection':
            current_step_idx = 0
        elif st.session_state.wizard_step == 'category_selection':
            current_step_idx = 1
        elif st.session_state.wizard_step == 'subcategory_selection':
            current_step_idx = 2
        
        # Create step indicator
        cols = st.columns(len(steps))
        for i, (col, step) in enumerate(zip(cols, steps)):
            with col:
                if i <= current_step_idx:
                    st.markdown(f"**{i+1}. {step}** ✅")
                else:
                    st.markdown(f"{i+1}. {step}")
    
    def render_card_selection(self):
        """Render the card selection step"""
        st.markdown("### 🏦 Which cards would you like to explore?")
        st.markdown("Select one or more cards to compare or learn about:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(
                f"{self.cards['icici_epm']['emoji']} {self.cards['icici_epm']['name']}", 
                key="select_icici",
                use_container_width=True
            ):
                st.session_state.selected_cards = ['icici_epm']
                st.session_state.wizard_step = 'category_selection'
                st.rerun()
        
        with col2:
            if st.button(
                f"{self.cards['axis_atlas']['emoji']} {self.cards['axis_atlas']['name']}", 
                key="select_axis",
                use_container_width=True
            ):
                st.session_state.selected_cards = ['axis_atlas']
                st.session_state.wizard_step = 'category_selection'
                st.rerun()
        
        with col3:
            if st.button(
                "🔄 Compare Both Cards", 
                key="select_both",
                use_container_width=True
            ):
                st.session_state.selected_cards = ['icici_epm', 'axis_atlas']
                st.session_state.wizard_step = 'category_selection'
                st.rerun()
    
    def render_category_selection(self):
        """Render the query category selection step"""
        st.markdown("### 🎯 What would you like to know about?")
        
        # Show selected cards
        card_names = [self.cards[card_id]['name'] for card_id in st.session_state.selected_cards]
        if len(card_names) == 1:
            st.info(f"Selected Card: **{card_names[0]}**")
        else:
            st.info(f"Comparing: **{' vs '.join(card_names)}**")
        
        # Render category buttons in a grid
        col1, col2 = st.columns(2)
        
        categories = list(self.query_categories.items())
        for i, (cat_id, cat_info) in enumerate(categories):
            col = col1 if i % 2 == 0 else col2
            with col:
                if st.button(
                    cat_info['name'],
                    key=f"cat_{cat_id}",
                    help=cat_info['description'],
                    use_container_width=True
                ):
                    st.session_state.selected_category = cat_id
                    if cat_id == 'other':
                        # Skip subcategory selection for 'other' and go straight to free-form
                        st.session_state.wizard_step = 'free_form'
                        st.session_state.wizard_complete = True
                    else:
                        st.session_state.wizard_step = 'subcategory_selection'
                    st.rerun()
        
        # Back button
        if st.button("← Back to Card Selection", key="back_to_cards"):
            st.session_state.wizard_step = 'card_selection'
            st.session_state.selected_cards = []
            st.rerun()
    
    def render_subcategory_selection(self):
        """Render the subcategory selection step"""
        category = st.session_state.selected_category
        cat_info = self.query_categories[category]
        
        st.markdown(f"### {cat_info['name']}")
        st.markdown(f"*{cat_info['description']}*")
        
        # Show selected cards
        card_names = [self.cards[card_id]['name'] for card_id in st.session_state.selected_cards]
        if len(card_names) == 1:
            st.info(f"Selected Card: **{card_names[0]}**")
        else:
            st.info(f"Comparing: **{' vs '.join(card_names)}**")
        
        # Render subcategory options
        if cat_info['subcategories']:
            st.markdown("**Select specific topic:**")
            
            for subcat_id, subcat_name in cat_info['subcategories'].items():
                if st.button(
                    subcat_name,
                    key=f"subcat_{subcat_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_subcategory = subcat_id
                    st.session_state.wizard_complete = True
                    st.rerun()
        else:
            # No subcategories, mark as complete
            st.session_state.wizard_complete = True
        
        # Back button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back to Categories", key="back_to_categories"):
                st.session_state.wizard_step = 'category_selection'
                st.session_state.selected_category = None
                st.rerun()
    
    def render_free_form_input(self):
        """Render free-form text input for 'other' category"""
        st.markdown("### 💬 Ask Anything Else")
        st.markdown("Ask any question about your selected cards using natural language:")
        
        # Show selected cards
        card_names = [self.cards[card_id]['name'] for card_id in st.session_state.selected_cards]
        if len(card_names) == 1:
            st.info(f"Selected Card: **{card_names[0]}**")
        else:
            st.info(f"Comparing: **{' vs '.join(card_names)}**")
        
        # Text input
        user_query = st.text_area(
            "Your Question:",
            placeholder="e.g., If I spend ₹2 lakhs on hotels, which card gives better rewards?",
            height=100
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Back to Categories", key="back_from_freeform"):
                st.session_state.wizard_step = 'category_selection'
                st.session_state.selected_category = None
                st.rerun()
        
        with col3:
            if st.button("Get Answer", key="submit_freeform", disabled=not user_query.strip()):
                if user_query.strip():
                    # Use existing QA engine for free-form queries
                    answer = self.qa_engine.get_answer(user_query)
                    st.markdown("### 🤖 Answer:")
                    st.markdown(answer)
        
        return user_query.strip() if user_query else None
    
    def generate_structured_answer(self) -> str:
        """Generate answer based on wizard selections"""
        category = st.session_state.selected_category
        subcategory = st.session_state.selected_subcategory
        selected_cards = st.session_state.selected_cards
        
        # Map wizard selections to QA engine queries
        query_map = {
            'rewards': {
                'general_rates': "What are the general reward rates?",
                'category_rates': "What are the category-specific reward rates?", 
                'comparison': "Compare reward rates between cards",
                'calculation': "How do I calculate rewards?"
            },
            'travel': {
                'lounge_access': "What are the airport lounge access benefits?",
                'travel_insurance': "What travel insurance coverage is provided?",
                'airport_benefits': "What are the airport benefits?",
                'airline_benefits': "What airline partnerships and benefits are available?"
            },
            'fees': {
                'annual_fee': "What is the annual fee and waiver conditions?",
                'surcharges': "What are the category surcharges?",
                'transaction_fees': "What are the transaction fees?",
                'other_fees': "What other fees are charged?"
            },
            'spending': {
                'hotels_travel': "What are the rewards and fees for hotel and travel spending?",
                'utilities': "What are the rewards and fees for utility payments?",
                'rent': "What are the rewards and fees for rent payments?",
                'fuel': "What are the rewards and fees for fuel purchases?",
                'education': "What are the rewards and fees for education payments?",
                'government': "What are the rewards and fees for government/tax payments?",
                'gold_jewellery': "What are the rewards and fees for gold and jewellery purchases?",
                'insurance': "What are the rewards and fees for insurance payments?",
                'gaming': "What are the rewards and fees for gaming transactions?",
                'wallet': "What are the rewards and fees for wallet/UPI transactions?"
            },
            'general': {
                'welcome_benefits': "What are the welcome and joining benefits?",
                'eligibility': "What are the eligibility criteria?",
                'milestones': "What are the milestone benefits?",
                'insurance_coverage': "What insurance coverage is provided?"
            }
        }
        
        # Build query based on selections
        if category in query_map and subcategory in query_map[category]:
            base_query = query_map[category][subcategory]
            
            # Add card-specific context if only one card selected
            if len(selected_cards) == 1:
                card_name = self.cards[selected_cards[0]]['name']
                query = f"{base_query} for {card_name}"
            else:
                query = base_query
        else:
            # Fallback query
            query = f"Tell me about {category}"
        
        # Use existing QA engine to get the answer
        return self.qa_engine.get_answer(query)
    
    def render_wizard(self):
        """Main wizard rendering function"""
        # Add a reset button in the sidebar
        with st.sidebar:
            if st.button("🔄 Start Over", key="reset_wizard"):
                self.reset_wizard()
                st.rerun()
            
            # Show current selections
            if st.session_state.selected_cards:
                st.markdown("**Selected Cards:**")
                for card_id in st.session_state.selected_cards:
                    st.markdown(f"• {self.cards[card_id]['name']}")
            
            if st.session_state.selected_category:
                st.markdown(f"**Category:** {self.query_categories[st.session_state.selected_category]['name']}")
            
            if st.session_state.selected_subcategory:
                category = st.session_state.selected_category
                subcategory = st.session_state.selected_subcategory
                if category in self.query_categories and subcategory in self.query_categories[category]['subcategories']:
                    st.markdown(f"**Topic:** {self.query_categories[category]['subcategories'][subcategory]}")
        
        # Render progress indicator
        if not st.session_state.wizard_complete:
            self.render_step_indicator()
            st.markdown("---")
        
        # Render current step
        if st.session_state.wizard_step == 'card_selection':
            self.render_card_selection()
        
        elif st.session_state.wizard_step == 'category_selection':
            self.render_category_selection()
        
        elif st.session_state.wizard_step == 'subcategory_selection':
            self.render_subcategory_selection()
        
        elif st.session_state.wizard_step == 'free_form':
            self.render_free_form_input()
        
        # Show answer when wizard is complete (except for free-form which handles its own display)
        if st.session_state.wizard_complete and st.session_state.wizard_step != 'free_form':
            st.markdown("---")
            st.markdown("### 🤖 Answer:")
            
            with st.spinner("Generating answer..."):
                answer = self.generate_structured_answer()
                st.markdown(answer)
            
            # Option to ask another question
            st.markdown("---")
            if st.button("Ask Another Question", key="ask_another"):
                self.reset_wizard()
                st.rerun() 