;;
#use "topfind"

;;
#require "unix"

;;
#require "astring"

open Astring

let read_file path =
  let inp = open_in path in
  let do_read () =
    let lines = ref [] in
    (try
       while true do
         lines := input_line inp :: !lines
       done
     with End_of_file -> ());
    List.rev !lines
  in
  Fun.protect ~finally:(fun () -> close_in inp) do_read

let parse_opt line =
  let line =
    match String.cut ~sep:"#" line with Some (l', _) -> l' | None -> line
  in
  let opt, value =
    match String.cut ~sep:"=" line with
    | Some (opt, value) -> (String.trim opt, Some (String.trim value))
    | None -> (String.trim line, None)
  in
  if opt = "" then None else Some (opt, value)

let parse_ocamlformat_file path = read_file path |> List.filter_map parse_opt

(** Recursively scan a directory, calls [f acc path] on every files. *)
let rec scan_dir f acc path =
  (* Don't recurse into symlinks. *)
  match Unix.lstat path with
  | { st_kind = S_REG; _ } -> f acc path
  | { st_kind = S_DIR; _ } ->
      let cnames = Sys.readdir path in
      Array.fold_left
        (fun acc cname -> scan_dir f acc (Filename.concat path cname))
        acc cnames
  | _ -> acc

let ocamlformat_files =
  let root = "." in
  Sys.readdir root
  |> Array.fold_left
       (fun acc name ->
         let path = Filename.concat root name in
         (* For each project, scan for [.ocamlformat] files. Keep the union of
            the options present to avoid over-representing some projects. *)
         let files =
           scan_dir
             (fun acc path ->
               if Filename.basename path = ".ocamlformat" then
                 parse_ocamlformat_file path :: acc
               else acc)
             [] path
         in
         if files = [] then acc
         else (name, List.sort_uniq compare (List.concat files)) :: acc)
       []

let () =
  Format.printf "%d projects@\n" (List.length ocamlformat_files);
  (* Count usage for each pair [option, value]. *)
  let tbl = Hashtbl.create 0 in
  List.iter
    (fun (project, options) ->
      List.iter
        (fun opt ->
          let p', n' =
            match Hashtbl.find_opt tbl opt with Some v -> v | None -> ([], 0)
          in
          Hashtbl.replace tbl opt (project :: p', n' + 1))
        options)
    ocamlformat_files;
  (* Print. *)
  Hashtbl.to_seq tbl |> List.of_seq
  |> List.sort (fun (_, (_, a)) (_, (_, b)) -> b - a)
  |> List.iter (fun ((opt, value), (projects, count)) ->
         let open Format in
         let pp_value ppf v = fprintf ppf " = %s" v in
         let pp_projects ppf = function
           | [] -> ()
           | _ :: _ as projects ->
               let pp_sep ppf () = fprintf ppf ", " in
               fprintf ppf " (%a)"
                 (pp_print_list ~pp_sep pp_print_string)
                 projects
         in
         (* For options with a count < 10, show the list of projects using it. *)
         printf "%4d %s%a%a@\n" count opt (pp_print_option pp_value) value
           pp_projects
           (if count < 10 then projects else []))
