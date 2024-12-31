import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class InventoryFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Create treeview
        columns = ('Date', 'Marques', 'Stock Précéden', 'Entrées', 'Sorties', 'Prix', 'Quantité Finale', 'Commentaire')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style='Modern.Treeview')
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add stock modification frame
        mod_frame = ttk.LabelFrame(self, text="Ajouter/Modifier Stock", style='Modern.TLabelframe')
        mod_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Stock modification form
        form_frame = ttk.Frame(mod_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Date field
        ttk.Label(form_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Name field
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=2, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=0, column=3, padx=5, pady=5)
        
        # Entries field
        ttk.Label(form_frame, text="Entrées:").grid(row=0, column=4, padx=5, pady=5)
        self.entries_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.entries_var).grid(row=0, column=5, padx=5, pady=5)
        
        # Price field
        ttk.Label(form_frame, text="Prix:").grid(row=0, column=6, padx=5, pady=5)
        self.price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.price_var).grid(row=0, column=7, padx=5, pady=5)
        
        # Comment field
        ttk.Label(form_frame, text="Commentaire:").grid(row=1, column=0, padx=5, pady=5)
        self.comment_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.comment_var).grid(row=1, column=1, columnspan=7, sticky='ew', padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(mod_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add buttons
        ttk.Button(buttons_frame, text="Enregistrer", command=self.save_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Ajouter", command=self.add_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Modifier", command=self.modify_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Supprimer", command=self.delete_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Rafraîchir", command=self.refresh_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Nettoyer Base", command=self.clear_database).pack(side=tk.RIGHT, padx=5)
        
        self.refresh_inventory()
    
    def save_stock(self):
        """Sauvegarder les modifications dans la base de données"""
        try:
            name = self.name_var.get()
            entries = int(self.entries_var.get() or 0)
            price = float(self.price_var.get() or 0)
            comment = self.comment_var.get()
            
            if not name:
                messagebox.showerror("Erreur", "Le nom est obligatoire!")
                return
                
            if self.db.save_motorcycle(name, entries, price):
                self.clear_form()
                self.refresh_inventory()
                messagebox.showinfo("Succès", "Stock sauvegardé avec succès!")
            else:
                messagebox.showerror("Erreur", "Erreur lors de la sauvegarde!")
        except ValueError:
            messagebox.showerror("Erreur", "Valeurs invalides!")
    
    def add_stock(self):
        """Ajouter un nouveau stock"""
        self.clear_form()
        self.name_var.set('')
    
    def modify_stock(self):
        """Modifier le stock sélectionné"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à modifier")
            return
            
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.name_var.set(values[1])  # Marques
        self.entries_var.set(values[3])  # Entrées
        self.price_var.set(values[5])  # Prix
        self.comment_var.set(values[7])  # Commentaire
    
    def delete_stock(self):
        """Supprimer le stock sélectionné"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à supprimer")
            return
            
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cet élément?"):
            item = self.tree.item(selection[0])
            name = item['values'][1]
            if self.db.delete_motorcycle(name):
                self.refresh_inventory()
                messagebox.showinfo("Succès", "Stock supprimé avec succès!")
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression!")
    
    def refresh_inventory(self):
        """Rafraîchir l'affichage de l'inventaire"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        inventory = self.db.get_inventory()
        for item in inventory:
            self.tree.insert('', 'end', values=(
                datetime.now().strftime("%Y-%m-%d"),
                item[0],  # name
                0,  # previous stock
                item[1],  # entries
                0,  # outputs
                f"{item[2]:.2f}",  # price
                item[1],  # final quantity
                ""  # comment
            ))
    
    def clear_form(self):
        """Nettoyer le formulaire"""
        self.name_var.set('')
        self.entries_var.set('')
        self.price_var.set('')
        self.comment_var.set('')
    
    def clear_database(self):
        """Nettoyer la base de données"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment nettoyer la base de données? Cette action est irréversible!"):
            if self.db.clear_database():
                self.refresh_inventory()
                messagebox.showinfo("Succès", "Base de données nettoyée avec succès!")
            else:
                messagebox.showerror("Erreur", "Erreur lors du nettoyage de la base de données!")